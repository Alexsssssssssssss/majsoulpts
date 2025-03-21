import re
from typing import Dict
from astrbot import Bot
from astrbot.model import Event
from astrbot.plugin import Plugin

class GameRoomPlugin(Plugin):
    def __init__(self, bot: Bot):
        super().__init__(bot)
        self.rooms: Dict[str, GameRoom] = {}
        
    class GameRoom:
        def __init__(self, code: str, creator: str):
            self.room_code = code
            self.members = [creator]
        
        def add_member(self, user_id: str) -> bool:
            if user_id in self.members or self.is_full():
                return False
            self.members.append(user_id)
            return True
        
        def is_full(self) -> bool:
            return len(self.members) >= 4

    def find_user_in_rooms(self, user_id: str) -> bool:
        return any(user_id in room.members for room in self.rooms.values())

    async def on_message(self, event: Event):
        msg = event.message.strip()
        
        # 匹配5位数字房间号
        if not re.fullmatch(r"^\d{5}$", msg):
            return
        
        user_id = event.user_id
        
        # 用户已存在其他房间
        if self.find_user_in_rooms(user_id):
            await self.bot.send(event, "⚠️ 您已经在其他房间中了！")
            return
        
        # 处理房间逻辑
        if msg in self.rooms:
            room = self.rooms[msg]
            if not room.add_member(user_id):
                await self.bot.send(event, "❌ 加入失败，房间可能已满或重复加入")
                return
            
            notice = f"@{event.user_name} 加入房间 {msg}\n当前人数：{len(room.members)}/4"
            
            if room.is_full():
                notice += "\n🚀 房间已满，游戏开始！"
                del self.rooms[msg]
            else:
                self.rooms[msg] = room
        else:
            # 创建新房间
            self.rooms[msg] = self.GameRoom(msg, user_id)
            notice = f"🎉 房间 {msg} 创建成功！\n@{event.user_name} 等待加入..."
        
        # 发送带@所有人的通知
        await self.bot.send(
            event,
            message=f"@everyone\n{notice}",
            parse_mention=True  # 启用@解析
        )

def setup(bot: Bot):
    bot.register_plugin(GameRoomPlugin(bot))
