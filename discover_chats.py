#!/usr/bin/env python3
"""
Discover ALL chat IDs that have messaged your bot
Works even if they're not in .env yet
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from telegram import Bot
from config import Config


async def discover_all_chats():
    """Find all chat IDs that have ever messaged the bot."""
    print("\n" + "="*60)
    print("DISCOVERING ALL CHAT IDs")
    print("="*60 + "\n")
    
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    
    try:
        bot_info = await bot.get_me()
        print(f"✓ Bot: @{bot_info.username} ({bot_info.first_name})")
        print()
        
        print("Fetching recent messages...")
        updates = await bot.get_updates(limit=100, offset=-100)
        
        if not updates:
            print("\n⚠️  No messages found!")
            print("\nMake sure people have:")
            print("  1. Searched for your bot: @" + bot_info.username)
            print("  2. Clicked 'Start'")
            print("  3. Sent a message")
            return
        
        print(f"✓ Found {len(updates)} message(s)\n")
        
        chats = {}
        for update in updates:
            if update.message:
                chat = update.message.chat
                chat_id = chat.id
                
                if chat_id not in chats:
                    chats[chat_id] = {
                        'id': chat_id,
                        'first_name': chat.first_name or '',
                        'last_name': chat.last_name or '',
                        'username': chat.username or '',
                        'type': chat.type
                    }
        
        print("="*60)
        print(f"FOUND {len(chats)} UNIQUE CHAT(S)")
        print("="*60 + "\n")
        
        current_ids = set(str(cid).strip() for cid in Config.TELEGRAM_CHAT_IDS if cid)
        
        for chat_id, info in chats.items():
            status = "✅ IN .env" if str(chat_id) in current_ids else "⭕ NEW"
            
            print(f"{status} Chat ID: {chat_id}")
            if info['first_name']:
                full_name = f"{info['first_name']} {info['last_name']}".strip()
                print(f"       Name: {full_name}")
            if info['username']:
                print(f"       Username: @{info['username']}")
            print(f"       Type: {info['type']}")
            print()
        
        print("="*60)
        print("FOR YOUR .env FILE:")
        print("="*60)
        all_ids = ','.join(str(cid) for cid in chats.keys())
        print(f"\nTELEGRAM_CHAT_IDS={all_ids}")
        print()
        
        new_ids = [cid for cid in chats.keys() if str(cid) not in current_ids]
        if new_ids:
            print(f"✨ {len(new_ids)} NEW chat ID(s) to add!")
            print(f"\nAdd these to your existing list:")
            for cid in new_ids:
                print(f"  - {cid}")
        else:
            print("✓ All chat IDs are already in your .env file")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                Chat ID Discovery Tool                         ║
║          Find everyone who messaged your bot                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(discover_all_chats())


if __name__ == "__main__":
    main()

