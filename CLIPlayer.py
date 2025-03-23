import urwid
import pygame
import os
import sys
import random

# Инициализация аудиосистемы
pygame.mixer.init()

class AudioPlayer:
    """Класс для управления аудио"""
    def __init__(self):
        self.current_file = None
        self.paused = False
        self.volume = 1.0  # Громкость от 0.0 до 1.0
        self.repeat = False  # Режим повтора
        self.shuffle = False  # Режим перемешки
        self.playlist = []  # Список файлов для воспроизведения
        self.current_index = 0  # Текущий индекс в плейлисте

    def load(self, filename):
        """Загрузка файла"""
        try:
            pygame.mixer.music.load(filename)
            self.current_file = filename
            pygame.mixer.music.set_volume(self.volume)
            return True
        except Exception as e:
            return False

    def play(self):
        """Начать воспроизведение"""
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.play()
            self.paused = False

    def pause(self):
        """Поставить на паузу"""
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def stop(self):
        """Остановить воспроизведение"""
        pygame.mixer.music.stop()
        self.paused = False

    def is_playing(self):
        """Проверка состояния воспроизведения"""
        return pygame.mixer.music.get_busy()

    def set_volume(self, volume):
        """Установка громкости"""
        self.volume = max(0.0, min(1.0, volume))  # Ограничение громкости
        pygame.mixer.music.set_volume(self.volume)

    def seek(self, seconds):
        """Перемотка на указанное количество секунд"""
        if self.current_file:
            current_pos = pygame.mixer.music.get_pos() / 1000  # Текущая позиция в секундах
            new_pos = max(0, current_pos + seconds)  # Новая позиция
            pygame.mixer.music.set_pos(new_pos)

    def toggle_repeat(self):
        """Переключение режима повтора"""
        self.repeat = not self.repeat

    def toggle_shuffle(self):
        """Переключение режима перемешки"""
        self.shuffle = not self.shuffle
        if self.shuffle:
            random.shuffle(self.playlist)
        else:
            self.playlist.sort()

    def next_track(self):
        """Следующий трек"""
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.load(self.playlist[self.current_index])
        self.play()

    def previous_track(self):
        """Предыдущий трек"""
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.load(self.playlist[self.current_index])
        self.play()

def get_audio_files(directory):
    """Получение списка аудиофайлов"""
    extensions = ('.mp3', '.wav', '.flac')
    return [os.path.join(directory, f) for f in os.listdir(directory) 
            if f.lower().endswith(extensions) and os.path.isfile(os.path.join(directory, f))]

class AudioPlayerUI:
    """Пользовательский интерфейс"""
    palette = [
        ('header', 'white', 'dark blue'),
        ('body', 'light gray', 'black'),
        ('button', 'black', 'light gray'),
        ('focus', 'white', 'dark red'),
    ]

    def __init__(self, directory='.'):
        self.directory = directory
        self.player = AudioPlayer()
        self.player.playlist = get_audio_files(self.directory)
        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Список файлов
        self.file_list = urwid.ListBox(
            urwid.SimpleFocusListWalker([
                urwid.AttrMap(
                    urwid.Button(f, self.on_file_select),
                    None, 'focus'
                ) for f in os.listdir(self.directory) if f.lower().endswith(('.mp3', '.wav', '.flac'))
            ])
        )

        # Кнопки управления
        self.play_btn = urwid.Button('Воспроизвести/Пауза', self.on_play_pause)
        self.stop_btn = urwid.Button('Стоп', self.on_stop)
        self.repeat_btn = urwid.Button('Повтор: Выкл', self.on_repeat)
        self.shuffle_btn = urwid.Button('Перемешка: Выкл', self.on_shuffle)
        self.volume_up_btn = urwid.Button('Громкость +', self.on_volume_up)
        self.volume_down_btn = urwid.Button('Громкость -', self.on_volume_down)
        controls = urwid.Columns([
            urwid.AttrMap(self.play_btn, 'button', 'focus'),
            urwid.AttrMap(self.stop_btn, 'button', 'focus'),
            urwid.AttrMap(self.repeat_btn, 'button', 'focus'),
            urwid.AttrMap(self.shuffle_btn, 'button', 'focus'),
            urwid.AttrMap(self.volume_up_btn, 'button', 'focus'),
            urwid.AttrMap(self.volume_down_btn, 'button', 'focus'),
        ])

        # Статусная строка
        self.status = urwid.Text(('header', " Статус: Остановлено "), align='center')

        # Основной макет
        self.layout = urwid.Frame(
            header=urwid.AttrMap(urwid.Text(f" Аудиопроигрыватель OpenUMP версия 1.0 | {self.directory}", align='center'), 'header'),
            body=urwid.AttrMap(self.file_list, 'body'),
            footer=urwid.Pile([
                urwid.AttrMap(controls, 'button'),
                urwid.Divider(),
                self.status
            ])
        )

    def update_status(self):
        """Обновление статусной строки"""
        status = []
        if self.player.paused:
            status.append("Пауза")
        elif self.player.is_playing():
            status.append("Воспроизведение")
        else:
            status.append("Остановлено")
        
        if self.player.current_file:
            status.append(f"Файл: {os.path.basename(self.player.current_file)}")
        
        self.status.set_text(('header', f" Статус: {' | '.join(status)} "))

    def on_file_select(self, button):
        """Обработчик выбора файла"""
        filename = os.path.join(self.directory, button.label)
        if self.player.load(filename):
            self.player.play()
            self.update_status()

    def on_play_pause(self, button):
        """Обработчик кнопки Воспроизвести/Пауза"""
        if self.player.current_file:
            if self.player.paused or not self.player.is_playing():
                self.player.play()
            else:
                self.player.pause()
            self.update_status()

    def on_stop(self, button):
        """Обработчик кнопки Стоп"""
        self.player.stop()
        self.update_status()

    def on_repeat(self, button):
        """Обработчик кнопки Повтор"""
        self.player.toggle_repeat()
        self.repeat_btn.set_label(f"Повтор: {'Вкл' if self.player.repeat else 'Выкл'}")

    def on_shuffle(self, button):
        """Обработчик кнопки Перемешка"""
        self.player.toggle_shuffle()
        self.shuffle_btn.set_label(f"Перемешка: {'Вкл' if self.player.shuffle else 'Выкл'}")

    def on_volume_up(self, button):
        """Обработчик кнопки Громкость +"""
        self.player.set_volume(self.player.volume + 0.1)
        self.update_status()

    def on_volume_down(self, button):
        """Обработчик кнопки Громкость -"""
        self.player.set_volume(self.player.volume - 0.1)
        self.update_status()

    def run(self):
        """Запуск приложения"""
        loop = urwid.MainLoop(
            self.layout,
            self.palette,
            unhandled_input=self.handle_input
        )
        loop.run()

    def handle_input(self, key):
        """Обработка клавиш"""
        if key in ('q', 'Q', 'й', 'Й'):  # Выход по клавише Q
            raise urwid.ExitMainLoop()
        elif key in ('s', 'S', 'ы', 'Ы'):  # Остановка по клавише S
            self.on_stop(None)
        elif key in ('p', 'P', 'з', 'З'):  # Воспроизведение/Пауза по клавише P
            self.on_play_pause(None)
        elif key == 'left':  # Перемотка назад на 10 секунд
            self.player.seek(-10)
        elif key == 'right':  # Перемотка вперед на 10 секунд
            self.player.seek(10)
        elif key in ('r', 'R', 'к', 'К'):  # Повтор по клавише R
            self.on_repeat(None)
        elif key in ('m', 'M', 'ь', 'Ь'):  # Перемешка по клавише M
            self.on_shuffle(None)

if __name__ == "__main__":
    # Получаем путь к папке из аргументов командной строки
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = '.'  # Текущая директория по умолчанию

    # Проверяем, существует ли папка
    if not os.path.isdir(directory):
        print(f"Ошибка: Папка '{directory}' не существует.")
        sys.exit(1)

    # Запуск программы
    AudioPlayerUI(directory).run()