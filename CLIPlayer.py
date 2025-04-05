import urwid
import vlc
import os
import sys
import random

class AudioPlayer:
    """Класс для управления аудио через VLC"""
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_file = None
        self.paused = False
        self.volume = 50  # Громкость от 0 до 100
        self.repeat = False
        self.shuffle = False
        self.playlist = []
        self.current_index = 0

    def load(self, filename):
        """Загрузка файла"""
        try:
            media = self.instance.media_new(filename)
            self.player.set_media(media)
            self.current_file = filename
            self.player.audio_set_volume(self.volume)
            return True
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return False

    def play(self):
        """Начать воспроизведение"""
        if self.player.get_media():
            self.player.play()
            self.paused = False

    def pause(self):
        """Поставить на паузу"""
        if self.player.is_playing():
            self.player.pause()
            self.paused = True

    def stop(self):
        """Остановить воспроизведение"""
        self.player.stop()
        self.paused = False

    def is_playing(self):
        """Проверка состояния воспроизведения"""
        return self.player.is_playing()

    def set_volume(self, volume):
        """Установка громкости (0-100)"""
        self.volume = max(0, min(100, volume))
        self.player.audio_set_volume(self.volume)

    def seek(self, seconds):
        """Перемотка (в секундах)"""
        if self.player.get_media():
            current_time = self.player.get_time() // 1000  # мс -> сек
            self.player.set_time((current_time + seconds) * 1000)

    def toggle_repeat(self):
        """Переключение повтора"""
        self.repeat = not self.repeat

    def toggle_shuffle(self):
        """Переключение перемешки"""
        self.shuffle = not self.shuffle
        if self.shuffle:
            random.shuffle(self.playlist)
        else:
            self.playlist.sort()

    def next_track(self):
        """Следующий трек"""
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.load(self.playlist[self.current_index])
            self.play()

    def previous_track(self):
        """Предыдущий трек"""
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load(self.playlist[self.current_index])
            self.play()

def get_audio_files(directory):
    """Получение списка аудиофайлов (поддерживает M4A, MP3 и др.)"""
    extensions = ('.mp3', '.wav', '.flac', '.m4a', '.aac')
    return [
        os.path.join(directory, f) 
        for f in os.listdir(directory) 
        if f.lower().endswith(extensions) and os.path.isfile(os.path.join(directory, f))
    ]

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
                ) for f in os.listdir(self.directory) 
                if f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.aac'))
            ])
        )

        # Кнопки управления
        self.play_btn = urwid.Button('▶/⏸', self.on_play_pause)
        self.stop_btn = urwid.Button('⏹', self.on_stop)
        self.repeat_btn = urwid.Button('🔁: Выкл', self.on_repeat)
        self.shuffle_btn = urwid.Button('🔀: Выкл', self.on_shuffle)
        self.vol_up_btn = urwid.Button('🔊+', self.on_volume_up)
        self.vol_down_btn = urwid.Button('🔉-', self.on_volume_down)
        
        controls = urwid.Columns([
            urwid.AttrMap(self.play_btn, 'button', 'focus'),
            urwid.AttrMap(self.stop_btn, 'button', 'focus'),
            urwid.AttrMap(self.repeat_btn, 'button', 'focus'),
            urwid.AttrMap(self.shuffle_btn, 'button', 'focus'),
            urwid.AttrMap(self.vol_up_btn, 'button', 'focus'),
            urwid.AttrMap(self.vol_down_btn, 'button', 'focus'),
        ])

        # Статусная строка
        self.status = urwid.Text(('header', " Статус: Остановлено | Громкость: 50% "), align='center')

        # Основной макет
        self.layout = urwid.Frame(
            header=urwid.AttrMap(urwid.Text(f"Аудиоплеер OpenUMP 2.0 | Папка: {self.directory}", align='center'), 'header'),
            body=urwid.AttrMap(self.file_list, 'body'),
            footer=urwid.Pile([
                controls,
                urwid.Divider(),
                self.status
            ])
        )

    def update_status(self):
        """Обновление статуса"""
        status = []
        if self.player.paused:
            status.append("⏸ Пауза")
        elif self.player.is_playing():
            status.append("▶ Воспроизведение")
        else:
            status.append("⏹ Остановлено")
        
        if self.player.current_file:
            status.append(f"📁: {os.path.basename(self.player.current_file)}")
        
        status.append(f"🔊: {self.player.volume}%")
        self.status.set_text(('header', " | ".join(status)))

    def on_file_select(self, button):
        """Выбор файла"""
        filename = os.path.join(self.directory, button.label)
        if self.player.load(filename):
            self.player.play()
            self.update_status()

    def on_play_pause(self, button):
        """Управление воспроизведением"""
        if self.player.current_file:
            if self.player.paused or not self.player.is_playing():
                self.player.play()
            else:
                self.player.pause()
            self.update_status()

    def on_stop(self, button):
        """Остановка"""
        self.player.stop()
        self.update_status()

    def on_repeat(self, button):
        """Повтор"""
        self.player.toggle_repeat()
        self.repeat_btn.set_label(f"🔁: {'Вкл' if self.player.repeat else 'Выкл'}")

    def on_shuffle(self, button):
        """Перемешка"""
        self.player.toggle_shuffle()
        self.shuffle_btn.set_label(f"🔀: {'Вкл' if self.player.shuffle else 'Выкл'}")

    def on_volume_up(self, button):
        """Увеличить громкость"""
        self.player.set_volume(self.player.volume + 10)
        self.update_status()

    def on_volume_down(self, button):
        """Уменьшить громкость"""
        self.player.set_volume(self.player.volume - 10)
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
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key in ('p', 'P'):
            self.on_play_pause(None)
        elif key in ('s', 'S'):
            self.on_stop(None)
        elif key == 'left':
            self.player.seek(-10)
        elif key == 'right':
            self.player.seek(10)
        elif key == '+':
            self.on_volume_up(None)
        elif key == '-':
            self.on_volume_down(None)

if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    if not os.path.isdir(directory):
        print(f"Ошибка: Папка '{directory}' не существует!")
        sys.exit(1)
    
    AudioPlayerUI(directory).run()