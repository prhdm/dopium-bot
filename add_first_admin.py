#!/usr/bin/env python3
"""
Script to add the first admin user to the database.
Usage: 
    python add_first_admin.py <user_id> [username] [full_name]
    python add_first_admin.py @username

Example:
    python add_first_admin.py 123456789
    python add_first_admin.py 123456789 prhdm "Full Name"
    python add_first_admin.py @prhdm
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import directly to avoid circular imports
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import only what we need
from infrastructure.database.sqlite_connection import get_db_connection


async def resolve_username_to_user_id(username: str) -> tuple:
    """
    Try to resolve username to user_id using bot API.
    Returns (user_id, full_name) or (None, None) if not found.
    """
    from telegram import Bot
    
    bot_token = os.getenv('BOT_TOKEN', '')
    if not bot_token:
        print("❌ BOT_TOKEN not found in .env file")
        return None, None
    
    bot = Bot(token=bot_token)
    username_clean = username.replace('@', '')
    
    # Try to get user from channel/group
    group_id = os.getenv('GROUP_ID', '')
    channel_id = os.getenv('CHANNEL_ID', '')
    channel_username = os.getenv('CHANNEL_USERNAME', '')
    
    user_id = None
    full_name = None
    
    # Try channel first (most likely place)
    if channel_username or channel_id:
        try:
            chat_id = channel_username.replace('@', '') if channel_username else channel_id
            member = await bot.get_chat_member(chat_id=chat_id, user_id=f"@{username_clean}")
            user_id = member.user.id
            full_name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
            print(f"✅ Found user in channel: {user_id}")
            return user_id, full_name
        except Exception as e:
            print(f"⚠️  Could not find user in channel: {e}")
    
    # Try group
    if not user_id and group_id:
        try:
            member = await bot.get_chat_member(chat_id=group_id, user_id=f"@{username_clean}")
            user_id = member.user.id
            full_name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
            print(f"✅ Found user in group: {user_id}")
            return user_id, full_name
        except Exception as e:
            print(f"⚠️  Could not find user in group: {e}")
    
    return None, None


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_first_admin.py <user_id> [username] [full_name]")
        print("   or: python add_first_admin.py @username")
        print("\nExample:")
        print("  python add_first_admin.py 123456789")
        print("  python add_first_admin.py 123456789 prhdm \"Full Name\"")
        print("  python add_first_admin.py @prhdm")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    # Check if it's a username (starts with @)
    if arg.startswith('@'):
        username = arg[1:]
        print(f"🔍 Trying to resolve username: @{username}")
        
        # Try to resolve username
        user_id, full_name = asyncio.run(resolve_username_to_user_id(username))
        
        if not user_id:
            print("\n❌ Could not resolve username to user_id.")
            print("\n💡 Solutions:")
            print("  1. Make sure the user is in your channel/group where the bot is admin")
            print("  2. Get the user_id manually:")
            print("     - Ask the user to send /start to your bot")
            print("     - Check the bot logs for their user_id")
            print("     - Or use @userinfobot to get their user_id")
            print("  3. Then use: python add_first_admin.py <user_id> @username")
            sys.exit(1)
    else:
        # Try to parse as user_id
        try:
            user_id = int(arg)
            username = sys.argv[2] if len(sys.argv) > 2 else None
            full_name = sys.argv[3] if len(sys.argv) > 3 else None
            
            # Remove @ from username if present
            if username and username.startswith('@'):
                username = username[1:]
        except ValueError:
            print("❌ Error: First argument must be a user_id (number) or username starting with @")
            print("\nExample:")
            print("  python add_first_admin.py 123456789")
            print("  python add_first_admin.py @prhdm")
            sys.exit(1)
    
    # Add admin directly to database
    db = get_db_connection()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    from datetime import datetime
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO admin_users 
            (user_id, username, full_name, created_at, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (user_id, username, full_name, datetime.now().isoformat()))
        
        conn.commit()
        success = True
    except Exception as e:
        print(f"❌ Database error: {e}")
        success = False
    
    if success:
        print(f"\n✅ Admin user {user_id} added successfully!")
        if username:
            print(f"   Username: @{username}")
        if full_name:
            print(f"   Full name: {full_name}")
        print("\n🎉 You can now use /admin command in the bot!")
    else:
        print("❌ Failed to add admin user")
        sys.exit(1)


if __name__ == "__main__":
    main()

