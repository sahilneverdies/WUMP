import discord
from discord.ext import commands
import aiosqlite
import asyncio
import datetime
import pytz

class AntiRoleDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_limits = {}
        self.cooldowns = {}

    async def is_blacklisted_guild(self, guild_id):
        async with aiosqlite.connect('db/block.db') as block_db:
            cursor = await block_db.execute("SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (str(guild_id),))
            return await cursor.fetchone() is not None

    async def fetch_audit_logs(self, guild, action):
        if not guild.me.guild_permissions.ban_members:
            return None
        try:
            async for entry in guild.audit_logs(action=action, limit=1):
                now = datetime.datetime.now(pytz.utc)
                created_at = entry.created_at
                difference = (now - created_at).total_seconds() * 1000

                if difference >= 3600000:
                    return None
                return entry
        except Exception:
            pass
        return None

    def can_fetch_audit(self, guild_id, event_name, max_requests=5, interval=10, cooldown_duration=300):
        now = datetime.datetime.now()
        self.event_limits.setdefault(guild_id, {}).setdefault(event_name, []).append(now)

        timestamps = self.event_limits[guild_id][event_name]
        timestamps = [t for t in timestamps if (now - t).total_seconds() <= interval]
        self.event_limits[guild_id][event_name] = timestamps

        if guild_id in self.cooldowns and event_name in self.cooldowns[guild_id]:
            if (now - self.cooldowns[guild_id][event_name]).total_seconds() < cooldown_duration:
                return False
            del self.cooldowns[guild_id][event_name]

        if len(timestamps) > max_requests:
            self.cooldowns.setdefault(guild_id, {})[event_name] = now
            return False

        return True

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        if await self.is_blacklisted_guild(guild.id):
            return

        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild.id,)) as cursor:
                antinuke_status = await cursor.fetchone()
            if not antinuke_status or not antinuke_status[0]:
                return

        if not self.can_fetch_audit(guild.id, 'role_delete'):
            return

        log_entry = await self.fetch_audit_logs(guild, discord.AuditLogAction.role_delete)
        if log_entry is None:
            return

        executor = log_entry.user

        if executor.id in {guild.owner_id, self.bot.user.id}:
            return

        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?", 
                                  (guild.id, executor.id)) as cursor:
                extra_owner_status = await cursor.fetchone()
            if extra_owner_status:
                return

            async with db.execute("SELECT rldl FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", 
                                  (guild.id, executor.id)) as cursor:
                whitelist_status = await cursor.fetchone()
            if whitelist_status and whitelist_status[0]:
                return

        await self.ban_executor_and_recreate_role(guild, executor, role)
        await asyncio.sleep(2)

    async def ban_executor_and_recreate_role(self, guild, executor, role):
        retries = 3
        while retries > 0:
            try:
                await self.ban_executor(guild, executor)
                await self.recreate_role(guild, role)
                return
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        await asyncio.sleep(float(retry_after))
                        retries -= 1
                else:
                    return
            except discord.errors.RateLimited as e:
                await asyncio.sleep(e.retry_after)
                retries -= 1
            except Exception:
                return
        return

    async def ban_executor(self, guild, executor):
        retries = 3
        while retries > 0:
            try:
                await guild.ban(executor, reason="Role Delete | Unwhitelisted User")
                return
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        await asyncio.sleep(float(retry_after))
                        retries -= 1
                else:
                    return
            except discord.errors.RateLimited as e:
                await asyncio.sleep(e.retry_after)
                retries -= 1
            except Exception:
                return
        return

    async def recreate_role(self, guild, role):
        try:
            await guild.create_role(
                name=role.name,
                permissions=role.permissions,
                color=role.color,
                hoist=role.hoist,
                mentionable=role.mentionable,
                reason="Role deleted by unwhitelisted user"
            )
        except discord.Forbidden:
            return
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = e.response.headers.get('Retry-After')
                if retry_after:
                    await asyncio.sleep(float(retry_after))
        except Exception:
            return
