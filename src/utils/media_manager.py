import os
from pathlib import Path
from typing import Optional, Union
import aiofiles
import aiohttp
from telegram import InputFile
import logging

class MediaManager:
    def __init__(self):
        self.base_path = Path('media')
        self.audio_path = self.base_path / 'audio'
        self.images_path = self.base_path / 'images'
        self.initialize_directories()
        
    def initialize_directories(self):
        """Создание необходимых директорий для медиафайлов"""
        self.audio_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        # Создаем поддиректории для разных типов аудио
        (self.audio_path / 'words').mkdir(exist_ok=True)
        (self.audio_path / 'dialogues').mkdir(exist_ok=True)
        (self.audio_path / 'exercises').mkdir(exist_ok=True)
        
        # Создаем поддиректории для разных типов изображений
        (self.images_path / 'words').mkdir(exist_ok=True)
        (self.images_path / 'grammar').mkdir(exist_ok=True)
        (self.images_path / 'achievements').mkdir(exist_ok=True)

    async def get_word_audio(self, word: str, module_id: int) -> Optional[InputFile]:
        """Получение аудиофайла произношения слова"""
        file_path = self.audio_path / 'words' / f'module_{module_id}' / f'{word}.mp3'
        if file_path.exists():
            return InputFile(file_path)
        return None
    
    async def get_word_image(self, word: str, module_id: int) -> Optional[InputFile]:
        """Получение изображения для слова"""
        file_path = self.images_path / 'words' / f'module_{module_id}' / f'{word}.jpg'
        if file_path.exists():
            return InputFile(file_path)
        return None
    
    async def save_audio(self, file_id: str, category: str, filename: str):
        """Сохранение аудиофайла"""
        try:
            category_path = self.audio_path / category
            category_path.mkdir(exist_ok=True)
            save_path = category_path / f'{filename}.mp3'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.telegram.org/file/bot{os.getenv("BOT_TOKEN")}/{file_id}') as response:
                    if response.status == 200:
                        async with aiofiles.open(save_path, mode='wb') as f:
                            await f.write(await response.read())
                    else:
                        raise Exception(f"Failed to download audio: {response.status}")
        except Exception as e:
            logging.error(f"Error saving audio file: {e}")
            raise
                        
    async def get_exercise_audio(self, exercise_id: int) -> Optional[InputFile]:
        """Получение аудиофайла для упражнения"""
        file_path = self.audio_path / 'exercises' / f'exercise_{exercise_id}.mp3'
        if file_path.exists():
            return InputFile(file_path)
        return None
    
    async def get_dialogue_audio(self, dialogue_id: int) -> Optional[InputFile]:
        """Получение аудиофайла диалога"""
        file_path = self.audio_path / 'dialogues' / f'dialogue_{dialogue_id}.mp3'
        if file_path.exists():
            return InputFile(file_path)
        return None
    
    async def get_achievement_image(self, achievement_id: int) -> Optional[InputFile]:
        """Получение изображения достижения"""
        file_path = self.images_path / 'achievements' / f'achievement_{achievement_id}.png'
        if file_path.exists():
            return InputFile(file_path)
        return None 