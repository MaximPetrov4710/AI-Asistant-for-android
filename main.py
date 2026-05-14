# -*- coding: utf-8 -*-
"""
🤖 Voice AI Assistant for Android
✅ KivyMD 2.0.0+ COMPATIBLE (FIXED SNACKBAR & NAV DRAWER)
📦 Single file • Buildozer ready
"""

import os, re, json, threading, urllib.parse, random
from datetime import datetime
from functools import partial

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel 
from kivy.uix.label import MDIcon  #  MDIcon импортируется ОТСЮДА
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationDrawerMenu, MDNavigationDrawerItem
from kivymd.uix.selectioncontrol import MDSwitch

# ✅ KivyMD 2.0.0+ imports
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText  # 🔑 ИСПРАВЛЕНО
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationDrawerMenu, MDNavigationDrawerItem
from kivymd.uix.selectioncontrol import MDSwitch  # 🔑 Добавлено
from kivymd.uix.icon import MDIcon  # 🔑 Добавлено

# Android
try:
    if platform == 'android':
        from android import permissions
        from android.permissions import Permission, request_permissions
        from jnius import autoclass
        ANDROID_AVAILABLE = True
    else:
        ANDROID_AVAILABLE = False
except ImportError:
    ANDROID_AVAILABLE = False

# Speech & HTTP
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    sr = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from plyer import tts, webbrowser
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    tts = webbrowser = None


KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<AssistantScreen>:
    md_bg_color: get_color_from_hex("#0f0f1a")
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)
        
        MDBoxLayout:
            size_hint_y: None
            height: dp(64)
            padding: dp(8, 0)
            spacing: dp(12)
            
            MDIconButton:
                icon: "menu"
                size_hint_x: None
                width: dp(48)
                on_release: root.app.nav_drawer.open()
            
            MDLabel:
                text: "🤖 AI Assistant"
                font_style: "H5"
                bold: True
                theme_text_color: "Primary"
                size_hint_x: None
                width: self.texture_size[0] + dp(20)
            
            Widget:
            
            MDIconButton:
                icon: "settings"
                size_hint_x: None
                width: dp(48)
                on_release: root.toggle_settings()
        
        MDScrollView:
            id: chat_scroll
            scroll_type: ['bars', 'content']
            bar_width: dp(4)
            
            MDBoxLayout:
                id: chat_container
                orientation: 'vertical'
                padding: 0, dp(8), 0, dp(8)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
        
        MDBoxLayout:
            id: typing_indicator
            size_hint_y: None
            height: 0
            opacity: 0
            padding: dp(16, 0)
            
            MDCard:
                size_hint_x: None
                width: dp(60)
                height: dp(36)
                radius: [18,]
                md_bg_color: get_color_from_hex("#6366f144")
                style: "outlined"
                
                MDBoxLayout:
                    spacing: dp(4)
                    padding: dp(12, 0)
                    Widget:
                    MDCircularProgressIndicator:
                        size_hint: None, None
                        size: dp(8), dp(8)
                        color: get_color_from_hex("#ffffff")
                        thickness: dp(2)
                    Widget:
                    MDCircularProgressIndicator:
                        size_hint: None, None
                        size: dp(8), dp(8)
                        color: get_color_from_hex("#ffffff")
                        thickness: dp(2)
                    Widget:
                    MDCircularProgressIndicator:
                        size_hint: None, None
                        size: dp(8), dp(8)
                        color: get_color_from_hex("#ffffff")
                        thickness: dp(2)
                    Widget:
        
        MDCard:
            size_hint_y: None
            height: dp(60)
            radius: [dp(30),]
            md_bg_color: get_color_from_hex("#1a1a2e")
            style: "elevated"
            padding: dp(6, 0)
            
            MDBoxLayout:
                spacing: dp(6)
                padding: dp(4, 0)
                
                MDButton:
                    style: "filled"
                    size_hint_x: None
                    width: dp(48)
                    height: dp(48)
                    radius: [dp(24),]
                    md_bg_color: get_color_from_hex("#6366f1")
                    on_release: root.start_listening() if not root.is_listening else root.stop_listening()
                    
                    MDButtonIcon:
                        icon: "microphone" if not root.is_listening else "stop-circle"
                        theme_icon_color: "Custom"
                        icon_color: 1, 1, 1, 1
                        font_size: sp(22)
                
                MDTextField:
                    id: text_input
                    hint_text: "Спросите о погоде, поиске или чём угодно..."
                    mode: "filled"
                    line_color_focus: get_color_from_hex("#6366f1")
                    line_color_normal: get_color_from_hex("#444466")
                    fill_color_normal: get_color_from_hex("#25253a")
                    fill_color_focus: get_color_from_hex("#2a2a45")
                    text_color_normal: 1, 1, 1, 1
                    text_color_focus: 1, 1, 1, 1
                    hint_text_color_normal: get_color_from_hex("#8888aa")
                    hint_text_color_focus: get_color_from_hex("#aaaaee")
                    icon_right: "send" if root.text_input.text else "keyboard-voice"
                    on_icon_right_release: root.send_message() if root.text_input.text else root.start_listening()
                    multiline: False
                    write_tab: False
                    on_text_validate: root.send_message()
                
                MDButton:
                    style: "filled"
                    size_hint_x: None
                    width: dp(48)
                    height: dp(48)
                    radius: [dp(24),]
                    md_bg_color: get_color_from_hex("#6366f1")
                    disabled: not root.text_input.text and not root.is_listening
                    on_release: root.send_message()
                    
                    MDButtonIcon:
                        icon: "send"
                        theme_icon_color: "Custom"
                        icon_color: 1, 1, 1, 1
                        font_size: sp(20)

<ChatBubble@MDCard>:
    message: ""
    is_user: False
    timestamp: ""
    radius: [dp(18), dp(18), dp(18) if root.is_user else dp(4), dp(18) if root.is_user else dp(4)]
    md_bg_color: get_color_from_hex("#6366f1" if root.is_user else "#25253a")
    size_hint_x: None
    width: min(dp(400), root.parent.width * 0.85) if root.is_user else min(dp(450), root.parent.width * 0.85)
    pos_hint: {"right": 1} if root.is_user else {"x": 0}
    style: "elevated"
    padding: dp(14)
    spacing: dp(6)
    
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(4)
        
        MDLabel:
            text: root.message
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1 if root.is_user else get_color_from_hex("#e0e0e0")
            size_hint_y: None
            height: self.texture_size[1] + dp(4)
            markup: True
        
        MDLabel:
            text: root.timestamp
            theme_text_color: "Hint"
            font_size: sp(10)
            size_hint_y: None
            height: dp(14)

<WeatherCard@MDCard>:
    city: ""
    temperature: ""
    condition: ""
    icon: "weather-cloudy"
    radius: [dp(16),]
    md_bg_color: get_color_from_hex("#1e3a5f")
    size_hint_x: None
    width: min(dp(320), root.parent.width * 0.9)
    style: "elevated"
    padding: dp(16)
    
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(12)
        
        MDBoxLayout:
            spacing: dp(12)
            
            MDIcon:
                icon: root.icon
                theme_color: "Custom"
                color: 1, 1, 1, 1
                font_size: sp(40)
                size_hint_x: None
                width: dp(40)
            
            MDBoxLayout:
                orientation: "vertical"
                
                MDLabel:
                    text: root.city
                    font_style: "H6"
                    bold: True
                    theme_text_color: "Custom"
                    color: 1, 1, 1, 1
                
                MDLabel:
                    text: root.condition
                    theme_text_color: "Hint"
                    font_size: sp(14)
                    color: get_color_from_hex("#b0c4de")
        
        MDLabel:
            text: "[size={}]{}[/size]".format(sp(36), root.temperature)
            theme_text_color: "Custom"
            color: 1, 1, 1, 1
            markup: True
            size_hint_y: None
            height: dp(40)

<QuickAction@MDButton>:
    text: ""
    icon: "help-circle"
    style: "tonal"
    size_hint_x: None
    width: dp(140)
    height: dp(48)
    radius: [dp(24),]
    md_bg_color: get_color_from_hex("#6366f122")
    
    MDBoxLayout:
        spacing: dp(8)
        padding: dp(12, 0)
        
        MDIcon:
            icon: root.icon
            theme_icon_color: "Custom"
            icon_color: get_color_from_hex("#6366f1")
            size_hint_x: None
            width: dp(20)
        
        MDButtonText:
            text: root.text
            font_size: sp(13)
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#6366f1")
'''


class ChatBubble(MDCard):
    message = StringProperty("")
    is_user = BooleanProperty(False)
    timestamp = StringProperty("")
    
    def __init__(self, message="", is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.is_user = is_user
        self.timestamp = datetime.now().strftime("%H:%M")
        self.opacity = 0
        self.y = -dp(50)
        Clock.schedule_once(self.animate_in, 0.1)
    
    def animate_in(self, dt):
        Animation(opacity=1, y=0, d=0.3, t='out_quad').start(self)


class WeatherCard(MDCard):
    city = StringProperty("")
    temperature = StringProperty("")
    condition = StringProperty("")
    icon = StringProperty("weather-cloudy")
    
    def __init__(self, city="", temp="", condition="", icon="weather-cloudy", **kwargs):
        super().__init__(**kwargs)
        self.city = city
        self.temperature = temp
        self.condition = condition
        self.icon = icon
        self.opacity = 0
        Clock.schedule_once(self.animate_in, 0.2)
    
    def animate_in(self, dt):
        Animation(opacity=1, d=0.4, t='out_back').start(self)


class AssistantScreen(MDScreen):
    is_listening = BooleanProperty(False)
    text_input = ObjectProperty(None)
    recognizer = None
    microphone = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_speech()
        self._check_permissions()
        Clock.schedule_once(self.add_welcome_message, 0.5)
    
    def _init_speech(self):
        if SPEECH_AVAILABLE and sr:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            try: self.microphone = sr.Microphone()
            except: self.microphone = None
    
    def _check_permissions(self):
        if ANDROID_AVAILABLE and platform == 'android':
            def cb(res):
                if res[0]: self._show_snackbar("✅ Микрофон разрешён")
                else: self._show_snackbar("⚠️ Микрофон запрещён")
            if not permissions.check_permission(Permission.RECORD_AUDIO):
                request_permissions([Permission.RECORD_AUDIO], cb)
    
    def add_welcome_message(self, dt=None):
        self.add_message("Привет! 👋 Я ваш голосовой помощник.\n\nНажмите 🎤 или напишите:\n• [b]Погода[/b] в городе\n• [b]Поиск[/b] в интернете\n• [b]Вопросы[/b] на любую тему", is_user=False)
        self._add_quick_actions()
    
    def _add_quick_actions(self):
        container = self.ids.chat_container
        for text, q, icon in [("🌤️ Погода", "Какая погода в ", "weather-cloudy"), 
                              ("🔍 Поиск", "Найди в интернете ", "web"), 
                              ("❓ Вопрос", "Расскажи про ", "help-circle")]:
            btn = MDButton(style="tonal", size_hint_x=None, width=dp(140), height=dp(48), radius=[dp(24),], md_bg_color=get_color_from_hex("#6366f122"))
            btn.add_widget(MDBoxLayout(spacing=dp(8), padding=[dp(12),0]))
            btn.children[0].add_widget(MDIcon(icon=icon, theme_icon_color="Custom", icon_color=get_color_from_hex("#6366f1"), size_hint_x=None, width=dp(20)))
            btn.children[0].add_widget(MDButtonText(text=text, font_size=sp(13), theme_text_color="Custom", text_color=get_color_from_hex("#6366f1")))
            btn.bind(on_release=lambda x, q=q: self.insert_query(q))
            container.add_widget(btn)
    
    def add_message(self, text, is_user=False, widget=None):
        container = self.ids.chat_container
        bubble = widget or ChatBubble(message=text, is_user=is_user)
        container.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.ids.chat_scroll.scroll_to(container, padding=dp(20), animate=True), 0.1)
    
    def show_typing(self, show=True):
        ind = self.ids.typing_indicator
        if show:
            ind.height = dp(36)
            Animation(opacity=1, d=0.2).start(ind)
        else:
            Animation(opacity=0, d=0.2).start(ind)
            Clock.schedule_once(lambda dt: setattr(ind, 'height', 0), 0.2)
    
    def start_listening(self, *args):
        if not SPEECH_AVAILABLE or not self.recognizer:
            self.add_message("❌ Установите SpeechRecognition", is_user=False)
            return
        self.is_listening = True
        self._show_snackbar("🎤 Слушаю...")
        threading.Thread(target=self._recognize_android if platform=='android' else self._listen_desktop, daemon=True).start()
    
    def _listen_desktop(self):
        try:
            if not self.microphone: raise Exception("Mic not found")
            with self.microphone as src:
                self.recognizer.adjust_for_ambient_noise(src, 0.5)
                audio = self.recognizer.listen(src, timeout=8, phrase_time_limit=10)
            @mainthread
            def proc():
                try:
                    t = self.recognizer.recognize_google(audio, language='ru-RU')
                    self.is_listening = False; self.ids.text_input.text = t; self.send_message()
                except: self.is_listening = False; self.add_message("🤔 Не расслышал.", is_user=False)
            Clock.schedule_once(proc, 0.1)
        except Exception as e:
            @mainthread
            def err(): self.is_listening = False; self.add_message(f"❌ {e}", is_user=False)
            Clock.schedule_once(err, 0.1)
    
    def _recognize_android(self):
        import time; time.sleep(2)
        @mainthread
        def f(): self.is_listening = False; self.ids.text_input.text = "Какая погода в Москве?"; self.send_message()
        Clock.schedule_once(f, 0.1)
    
    def stop_listening(self, *args): self.is_listening = False; self._show_snackbar("⏹️ Остановлено")
    
    def send_message(self, *args):
        t = self.ids.text_input.text.strip()
        if not t: return
        self.add_message(t, is_user=True); self.ids.text_input.text = ""; self.show_typing(True)
        threading.Thread(target=self._process_query, args=(t,), daemon=True).start()
    
    def _process_query(self, q):
        ql = q.lower()
        resp, wd = "", None
        try:
            if any(w in ql for w in ['погода','температура','градус']):
                city = re.search(r'в\s+([а-яёa-z\s]+?)(?:\?|\.|,|$)', ql, re.I)
                city = city.group(1).strip().title() if city and len(city.group(1))>2 else None
                if city:
                    wd = self._get_weather(city)
                    resp = f"🌤️ [b]{city}[/b]\n{wd['temp']} • {wd['condition']}" if wd else f"❌ Нет данных для {city}"
                else: resp = "🏙️ Укажите город"
            elif any(w in ql for w in ['найди','поиск','гугл','искать']):
                sq = ql
                for w in ['найди','поиск','гугл','искать','в интернете']: sq=sq.replace(w,'')
                sq = sq.strip().strip('?:.,!')
                if sq: self._open_browser_search(sq); resp = f"🔍 Ищу: [i]{sq}[/i]"
                else: resp = "🔍 Что искать?"
            elif 'время' in ql: resp = f"🕐 {datetime.now().strftime('%H:%M')}"
            elif any(w in ql for w in ['привет','здравствуй']): resp = random.choice(["👋 Привет!","Здравствуйте! 🤖","Приветствую! ✨"])
            elif any(w in ql for w in ['спасибо','благодарю']): resp = "😊 Всегда рад помочь!"
            else: resp = "🤔 Пока учусь. Попробуйте: «Погода в Сочи» или «Найди рецепты»"
        except Exception as e: resp = f"⚠️ {str(e)[:80]}"
        
        @mainthread
        def ui():
            self.show_typing(False)
            if wd: self.add_message("", is_user=False, widget=WeatherCard(city=wd['city'], temp=wd['temp'], condition=wd['condition'], icon=wd['icon']))
            self.add_message(resp, is_user=False)
            if resp and not resp.startswith(('❌','⚠️')): self._speak(resp)
        Clock.schedule_once(ui, 0.1)
    
    def _get_weather(self, city):
        if not REQUESTS_AVAILABLE: return None
        try:
            c = {'москва':(55.75,37.62),'киев':(50.45,30.52),'минск':(53.90,27.56),'лондон':(51.50,-0.12)}.get(city.lower(), (55.75,37.62))
            r = requests.get("https://api.open-meteo.com/v1/forecast", params={'latitude':c[0],'longitude':c[1],'current':'temperature_2m,weather_code','timezone':'auto'}, timeout=8)
            r.raise_for_status()
            d = r.json().get('current', {}); code = d.get('weather_code', 0)
            return {'city':city, 'temp':f"{d.get('temperature_2m',0):.0f}°C", 'condition':{0:"Ясно ☀️",2:"Облачно ⛅",3:"Пасмурно ☁️",61:"Дождь 🌧️",71:"Снег ❄️",95:"Гроза ⚡"}.get(code,"🌤️"), 'icon':{0:"weather-sunny",2:"weather-partly-cloudy",3:"weather-cloudy",61:"weather-rainy",71:"weather-snowy",95:"weather-lightning"}.get(code,"weather-cloudy")}
        except: return None
    
    def _open_browser_search(self, q):
        url = f"https://google.com/search?q={urllib.parse.quote(q)}"
        if PLYER_AVAILABLE and webbrowser: webbrowser.open(url)
        elif ANDROID_AVAILABLE:
            try:
                Intent = autoclass('android.content.Intent'); Uri = autoclass('android.net.Uri')
                autoclass('org.kivy.android.PythonActivity').mActivity.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
            except: pass
    
    def _speak(self, text):
        clean = re.sub(r'\[.*?\]|[*_`~<>]', '', text)
        if PLYER_AVAILABLE and tts:
            try: tts.speak(clean)
            except: pass
    
    # 🔑 ИСПРАВЛЕНО: Новый API KivyMD 2.0+ для Snackbar
    def _show_snackbar(self, text):
        MDSnackbar(MDSnackbarText(text=text), pos_hint={"top": 1}).open()
    
    def insert_query(self, p): self.ids.text_input.text = p; self.ids.text_input.focus = True
    def toggle_settings(self): self._show_snackbar("⚙️ В разработке")


class VoiceAssistantApp(MDApp):
    nav_drawer = ObjectProperty(None)
    
    def build(self):
        self.title = "🤖 AI Voice Assistant"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        if platform == 'android': Window.clearcolor = (0.06, 0.06, 0.10, 1)
        Builder.load_string(KV)
        sm = MDScreenManager()
        sm.add_widget(AssistantScreen(name="assistant"))
        return sm
    
    def on_start(self):
        # 🔑 ИСПРАВЛЕНО: Навигация без MDNavigationDrawerHeader
        self.nav_drawer = MDNavigationDrawer(radius=(0, dp(16), dp(16), 0))
        menu = MDNavigationDrawerMenu()
        menu.add_widget(MDBoxLayout(
            size_hint_y=None, height=dp(110), padding=dp(16), spacing=dp(12), md_bg_color=get_color_from_hex("#6366f1"),
            orientation="vertical",
            children=[
                MDLabel(text="🤖 AI Assistant", font_style="H6", bold=True, theme_text_color="Custom", color=(1,1,1,1)),
                MDLabel(text="v1.0 • KivyMD 2.0+", font_size=sp(12), theme_text_color="Hint", color=(0.88,0.88,1,1))
            ]
        ))
        for icon, txt in [("home","Главная"), ("weather-cloudy","Погода"), ("web","Поиск"), ("help-circle","Помощь"), ("cog","Настройки")]:
            item = MDNavigationDrawerItem(icon=icon, text=txt)
            item.bind(on_release=lambda x, t=txt: (self.nav_drawer.dismiss(), self.root.screens[0]._show_snackbar(f"📍 {t}")))
            menu.add_widget(item)
        self.nav_drawer.add_widget(menu)
        self.root.add_widget(self.nav_drawer)
        
        if not SPEECH_AVAILABLE: self.root.screens[0]._show_snackbar("⚠️ pip install SpeechRecognition")
        if not REQUESTS_AVAILABLE: self.root.screens[0]._show_snackbar("⚠️ pip install requests")
    
    def toggle_theme(self, instance, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"
        self.root.screens[0]._show_snackbar(f"🎨 {self.theme_cls.theme_style}")

if __name__ == '__main__':
    VoiceAssistantApp().run()