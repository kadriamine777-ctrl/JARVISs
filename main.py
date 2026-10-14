from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.clock import Clock
import os, threading, re
from datetime import datetime

try:
    from plyer import vibrator, flash
    PLYER_OK = True
except:
    PLYER_OK = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except:
    PIL_OK = False

try:
    from moviepy.editor import ImageClip, concatenate_videoclips
    MONTAJ_OK = True
except Exception as e:
    MONTAJ_OK = False
    MOVIEPY_ERROR = str(e)

Window.clearcolor = (0.05, 0.05, 0.08, 1)

class JarvisUltimate(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        
        self.add_widget(Label(text='[b]JARVIS ULTIMATE V4[/b]\nExecute Any Command + Montage + Video From Script', markup=True, size_hint_y=0.15, font_size='16sp', color=(0, 0.8, 1, 1)))
        
        self.status = Label(text='Ready...', size_hint_y=0.08, color=(0,1,0,1))
        self.add_widget(self.status)

        tabs = TabbedPanel(do_default_tab=False)
        
        tab1 = TabbedPanelItem(text='EXECUTE')
        box1 = BoxLayout(orientation='vertical', spacing=5)
        self.cmd_input = TextInput(hint_text='open youtube, camera, flash on, vibrate', size_hint_y=0.3, multiline=False)
        self.cmd_input.bind(on_text_validate=self.execute_command)
        box1.add_widget(self.cmd_input)
        box1.add_widget(Button(text='RUN', size_hint_y=0.2, background_color=(0,0.8,1,1), on_press=self.execute_command))
        self.cmd_output = TextInput(text='Output here...', readonly=True, size_hint_y=0.5)
        box1.add_widget(self.cmd_output)
        tab1.add_widget(box1)
        tabs.add_widget(tab1)

        tab2 = TabbedPanelItem(text='VIDEO SCRIPT')
        box2 = BoxLayout(orientation='vertical', spacing=5)
        self.script_input = TextInput(hint_text='[SCENE 1 - 3s]\nTEXT: Hello I am Jarvis\nBG: black\n\n[SCENE 2 - 5s]\nTEXT: This video from script\nBG: blue', size_hint_y=0.6)
        box2.add_widget(self.script_input)
        btn_gen = Button(text='GENERATE VIDEO', size_hint_y=0.2, background_color=(1,0.5,0,1), on_press=self.generate_video_from_script)
        box2.add_widget(btn_gen)
        self.video_status = Label(text='Write script and press generate', size_hint_y=0.2, color=(1,1,0,1))
        box2.add_widget(self.video_status)
        tab2.add_widget(box2)
        tabs.add_widget(tab2)

        tab3 = TabbedPanelItem(text='MONTAGE')
        box3 = BoxLayout(orientation='vertical')
        montaj_text = f"Montage: {'OK' if MONTAJ_OK else 'Disabled'}\nPlyer: {'OK' if PLYER_OK else 'No'}\nPIL: {'OK' if PIL_OK else 'No'}"
        box3.add_widget(Label(text=montaj_text))
        box3.add_widget(Button(text='Test Vibrate', on_press=self.test_vibrate))
        box3.add_widget(Button(text='Test Flash', on_press=self.test_flash))
        tab3.add_widget(box3)
        tabs.add_widget(tab3)

        tabs.default_tab = tab1
        self.add_widget(tabs)

    def log(self, txt):
        self.cmd_output.text += f"\n[{datetime.now().strftime('%H:%M:%S')}] {txt}"
        self.status.text = txt

    def execute_command(self, *args):
        cmd = self.cmd_input.text.lower().strip()
        if not cmd:
            return
        self.log(f"Exec: {cmd}")
        try:
            if 'youtube' in cmd:
                import webbrowser
                webbrowser.open('https://youtube.com')
                self.log("YouTube opened")
            elif 'flash on' in cmd:
                if PLYER_OK:
                    try: flash.on()
                    except: pass
                self.log("Flash ON")
            elif 'flash off' in cmd:
                if PLYER_OK:
                    try: flash.off()
                    except: pass
                self.log("Flash OFF")
            elif 'vibrate' in cmd:
                if PLYER_OK:
                    try: vibrator.vibrate(1)
                    except: pass
                self.log("Vibrate")
            elif 'camera' in cmd:
                self.log("Camera command")
            elif 'exec:' in cmd:
                code = cmd.replace('exec:', '').strip()
                exec(code)
                self.log(f"Code executed: {code}")
            else:
                self.log(f"Done: {cmd}")
                if PLYER_OK:
                    try: vibrator.vibrate(0.2)
                    except: pass
        except Exception as e:
            self.log(f"Error: {e}")

    def test_vibrate(self, *a):
        try:
            if PLYER_OK:
                vibrator.vibrate(0.5)
                self.log("Vibrate OK")
        except Exception as e:
            self.log(f"Vibrate error: {e}")

    def test_flash(self, *a):
        try:
            if PLYER_OK:
                flash.on()
                Clock.schedule_once(lambda dt: flash.off(), 2)
                self.log("Flash OK")
        except Exception as e:
            self.log(f"Flash error: {e}")

    def generate_video_from_script(self, *a):
        if not PIL_OK:
            self.video_status.text = "Pillow not installed"
            return
        if not MONTAJ_OK:
            self.video_status.text = "Montage disabled, generating image"
            self.generate_images_only()
            return

        script = self.script_input.text.strip()
        if not script:
            self.video_status.text = "Write script first"
            return

        self.video_status.text = "Generating video... wait"
        
        def run():
            try:
                pattern = r'\[SCENE\s*(\d+)\s*-\s*(\d+)s?\]\s*TEXT:\s*(.*?)\s*BG:\s*(.*?)(?=\[SCENE|\Z)'
                matches = re.findall(pattern, script, re.DOTALL | re.IGNORECASE)
                
                if not matches:
                    Clock.schedule_once(lambda dt: setattr(self.video_status, 'text', "Wrong format"), 0)
                    return

                clips = []
                tmp_dir = "/tmp"
                if not os.path.exists(tmp_dir):
                    tmp_dir = "/sdcard"
                
                for num, dur, text, bg in matches:
                    dur = int(dur)
                    text = text.strip()
                    bg = bg.strip().lower()
                    
                    color_map = {'black': (0,0,0), 'blue': (0,0,255), 'red': (255,0,0), 'green': (0,255,0), 'white': (255,255,255), 'yellow': (255,255,0)}
                    bg_color = color_map.get(bg, (20,20,40))
                    
                    img = Image.new('RGB', (720, 1280), bg_color)
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype("/system/fonts/DroidSans.ttf", 40)
                    except:
                        font = ImageFont.load_default()
                    
                    words = text.split()
                    lines = []
                    cur = ""
                    for w in words:
                        if len(cur + " " + w) < 25:
                            cur += " " + w
                        else:
                            lines.append(cur)
                            cur = w
                    lines.append(cur)
                    
                    y = 500
                    for line in lines:
                        bbox = draw.textbbox((0,0), line, font=font)
                        w = bbox[2]-bbox[0]
                        draw.text(((720-w)/2, y), line, fill=(255,255,255), font=font)
                        y += 60
                    
                    temp_path = f"{tmp_dir}/scene_{num}.jpg"
                    img.save(temp_path)
                    clip = ImageClip(temp_path, duration=dur)
                    clips.append(clip)
                
                if clips:
                    final = concatenate_videoclips(clips)
                    output_path = "/sdcard/JARVIS_video.mp4"
                    final.write_videofile(output_path, fps=24, codec='libx264')
                    Clock.schedule_once(lambda dt: setattr(self.video_status, 'text', f"Done: {output_path}"), 0)
                    
            except Exception as e:
                err = str(e)[:200]
                Clock.schedule_once(lambda dt: setattr(self.video_status, 'text', f"Error: {err}"), 0)
        
        threading.Thread(target=run, daemon=True).start()

    def generate_images_only(self):
        try:
            script = self.script_input.text
            img = Image.new('RGB', (720, 1280), (20,20,40))
            draw = ImageDraw.Draw(img)
            draw.text((50, 500), script[:200], fill=(255,255,255))
            img.save("/sdcard/JARVIS_image.jpg")
            self.video_status.text = "Image saved (moviepy disabled)"
        except Exception as e:
            self.video_status.text = f"Error: {e}"

class JarvisApp(App):
    def build(self):
        return JarvisUltimate()

if __name__ == '__main__':
    JarvisApp().run()
