import cv2
import mediapipe as mp
import numpy as np
import time
import random
import os

# MediaPipe el algılama modülünü başlat
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Kamerayı başlat
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera acilamadi!")
    exit()

screen_width = 1280
screen_height = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

game_state = "MENU" 
countdown_start = 0
game_start_time = 0
game_duration = 60  
score = 0
right_hand_position = None
left_hand_position = None
last_button_press_time = 0
button_cooldown = 1.0

right_target = (int(screen_width * 0.7), int(screen_height * 0.5))
left_target = (int(screen_width * 0.3), int(screen_height * 0.5))
target_radius = 30

restart_button = {"x": 20, "y": 50, "width": 100, "height": 40, "text": "Yeniden Basla", "active": False}
pause_button = {"x": screen_width - 120, "y": 50, "width": 100, "height": 40, "text": "Duraklat", "active": False}
resume_button = {"x": screen_width - 120, "y": 50, "width": 100, "height": 40, "text": "Devam Et", "active": False}
menu_button = {"x": screen_width // 2 - 50, "y": screen_height - 70, "width": 100, "height": 40, "text": "Ana Menu", "active": False}
play_button = {"x": screen_width // 2 - 50, "y": screen_height // 2, "width": 100, "height": 40, "text": "Oyna", "active": False}

script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    left_balloon_path = os.path.join(script_dir, "images", "ballon.png")
    right_balloon_path = os.path.join(script_dir, "images", "ballon.png")

    
    left_balloon_exists = os.path.exists(left_balloon_path)
    right_balloon_exists = os.path.exists(right_balloon_path)
    
    if left_balloon_exists:
        left_balloon_img = cv2.imread(left_balloon_path, cv2.IMREAD_UNCHANGED)
        # Balon boyutunu ayarla
        left_balloon_size = 60
        left_balloon_img = cv2.resize(left_balloon_img, (left_balloon_size, left_balloon_size))
    
    if right_balloon_exists:
        right_balloon_img = cv2.imread(right_balloon_path, cv2.IMREAD_UNCHANGED)
        # Balon boyutunu ayarla
        right_balloon_size = 60
        right_balloon_img = cv2.resize(right_balloon_img, (right_balloon_size, right_balloon_size))
    
    print("Balonlar yuklendi" if (left_balloon_exists and right_balloon_exists) else "Bazi balonlar yuklenemedi, daire kullanilacak.")
    
except Exception as e:
    print(f"Gorsel yukleme hatasi: {e}")
    left_balloon_exists = False
    right_balloon_exists = False

# Balon/Elma sınıfı
class Balloon:
    def __init__(self, screen_width):
        self.size = 60  # Görsel boyutu
        self.radius = 30  # Çarpışma kontrolü için hala kullanılacak
        self.x = random.randint(self.size//2, screen_width - self.size//2)
        self.y = -self.size//2
        self.speed = random.uniform(3, 7)
        self.color = (0, 0, 255)  # Yedek renk (görsel yüklenemediğinde kullanılır)
        self.side = "left" if self.x < screen_width // 2 else "right"
        self.collected = False
        
    def update(self):
        self.y += self.speed
        
    def draw(self, img):
        # Her zaman görsel kullanmayı dene, sadece yüklenemediyse daireye geri dön
        if (self.side == "left" and left_balloon_exists) or (self.side == "right" and right_balloon_exists):
            balloon_img = left_balloon_img if self.side == "left" else right_balloon_img
            
            # Görseli yerleştir
            y_start = max(0, int(self.y - self.size//2))
            y_end = min(screen_height, int(self.y + self.size//2))
            x_start = max(0, int(self.x - self.size//2))
            x_end = min(screen_width, int(self.x + self.size//2))
            
            # Görselin görünür kısmını hesapla
            img_y_start = max(0, 0 - (self.y - self.size//2))
            img_x_start = max(0, 0 - (self.x - self.size//2))
            img_y_end = img_y_start + (y_end - y_start)
            img_x_end = img_x_start + (x_end - x_start)
            
            # Görsel sınırları kontrol et
            if y_end > y_start and x_end > x_start and img_y_end > img_y_start and img_x_end > img_x_start:
                try:
                    # RGBA görsel ise (4 kanal)
                    if balloon_img.shape[2] == 4:
                        # Alfa kanalı olan PNG dosyası
                        alpha_s = balloon_img[img_y_start:img_y_end, img_x_start:img_x_end, 3] / 255.0
                        alpha_l = 1.0 - alpha_s
                        
                        for c in range(0, 3):
                            img[y_start:y_end, x_start:x_end, c] = (alpha_s * balloon_img[img_y_start:img_y_end, img_x_start:img_x_end, c] + 
                                                                  alpha_l * img[y_start:y_end, x_start:x_end, c])
                    else:
                        # Normal görsel (3 kanal)
                        img[y_start:y_end, x_start:x_end] = balloon_img[img_y_start:img_y_end, img_x_start:img_x_end]
                except Exception as e:
                    # Hata olursa daireye geri dön
                    print(f"Balon cizme hatasi: {e}")
                    cv2.circle(img, (int(self.x), int(self.y)), self.radius, self.color, -1)
            else:
                cv2.circle(img, (int(self.x), int(self.y)), self.radius, self.color, -1)
        else:
            # Görsel yoksa daire çiz
            cv2.circle(img, (int(self.x), int(self.y)), self.radius, self.color, -1) 
    
    def is_collected(self, finger_tip_x, finger_tip_y, hand_side):
        if self.collected:
            return False
        
        # Doğru el ile mi yakalanıyor?
        correct_hand = (self.side == hand_side)
        
        # Parmak ucu ile balon arasındaki mesafeyi hesapla
        distance = np.sqrt((self.x - finger_tip_x)**2 + (self.y - finger_tip_y)**2)
        
        # Toplama koşulu: mesafe < balon yarıçapı + parmak ucu noktası yarıçapı ve doğru el
        if distance < self.radius + 10 and correct_hand:
            self.collected = True
            return True
        return False

# Butonu çiz
def draw_button(img, button):
    color = (0, 255, 0) if button["active"] else (0, 120, 255)
    cv2.rectangle(img, (button["x"], button["y"]), 
                 (button["x"] + button["width"], button["y"] + button["height"]), 
                 color, -1)
    cv2.rectangle(img, (button["x"], button["y"]), 
                 (button["x"] + button["width"], button["y"] + button["height"]), 
                 (255, 255, 255), 2)
    
    # Metin boyutunu belirle
    text_size = cv2.getTextSize(button["text"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
    text_x = button["x"] + (button["width"] - text_size[0]) // 2
    text_y = button["y"] + (button["height"] + text_size[1]) // 2
    
    cv2.putText(img, button["text"], (text_x, text_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# Buton basıldı mı kontrol et
def is_button_pressed(finger_tip, button):
    if finger_tip is None:
        return False
    
    x, y = finger_tip
    
    return (button["x"] <= x <= button["x"] + button["width"] and 
            button["y"] <= y <= button["y"] + button["height"])

# Balon listesi
balloons = []
last_balloon_time = 0
balloon_spawn_interval = 1.0  # saniye

# Ana döngü
while True:
    # Kameradan bir kare oku
    success, img = cap.read()
    if not success:
        print("Kare okunamadi!")
        break
    
    # Görüntüyü yatay olarak çevir (ayna görüntüsü)
    img = cv2.flip(img, 1)
    
    # Görüntüyü BGR'den RGB'ye çevir (MediaPipe RGB bekler)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Elleri algıla
    results = hands.process(img_rgb)
    
    # Sağ ve sol el pozisyonlarını ve işaret parmağı uçlarını bul
    right_index_tip = None
    left_index_tip = None
    right_hand_found = False
    left_hand_found = False
    
    if results.multi_hand_landmarks:
        # Elde edilen el işaretleri
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # El pozisyonları (işaret parmağının ucu)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_finger_tip.x * screen_width)
            y = int(index_finger_tip.y * screen_height)
            
            # Sağ/sol el tespiti
            if results.multi_handedness and len(results.multi_handedness) > idx:
                handedness = results.multi_handedness[idx]
                if handedness.classification[0].label == "Right":
                    right_hand_position = (x, y)
                    right_index_tip = (x, y)
                    right_hand_found = True
                else:
                    left_hand_position = (x, y)
                    left_index_tip = (x, y)
                    left_hand_found = True
            
            # El işaretlerini çiz
            mp_drawing.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
            )
    
    # Buton aktivasyon durumlarını güncelle
    restart_button["active"] = is_button_pressed(right_index_tip, restart_button) or is_button_pressed(left_index_tip, restart_button)
    pause_button["active"] = is_button_pressed(right_index_tip, pause_button) or is_button_pressed(left_index_tip, pause_button)
    resume_button["active"] = is_button_pressed(right_index_tip, resume_button) or is_button_pressed(left_index_tip, resume_button)
    menu_button["active"] = is_button_pressed(right_index_tip, menu_button) or is_button_pressed(left_index_tip, menu_button)
    play_button["active"] = is_button_pressed(right_index_tip, play_button) or is_button_pressed(left_index_tip, play_button)
    
    # Buton basılma işlemleri (soğuma süresi ile)
    current_time = time.time()
    if current_time - last_button_press_time > button_cooldown:
        if game_state == "MENU" and play_button["active"]:
            game_state = "WAITING_FOR_HANDS"
            last_button_press_time = current_time
        
        elif game_state == "PLAYING" and pause_button["active"]:
            game_state = "PAUSED"
            last_button_press_time = current_time
        
        elif game_state == "PAUSED" and resume_button["active"]:
            game_state = "PLAYING"
            # Duraklama süresini telafi et
            game_start_time = time.time() - (last_button_press_time - game_start_time)
            last_button_press_time = current_time
        
        elif (game_state == "GAME_OVER" or game_state == "PAUSED") and restart_button["active"]:
            game_state = "WAITING_FOR_HANDS"
            score = 0
            balloons = []
            last_button_press_time = current_time
        
        elif (game_state == "GAME_OVER" or game_state == "PAUSED") and menu_button["active"]:
            game_state = "MENU"
            score = 0
            balloons = []
            last_button_press_time = current_time
    
    # Oyun durumuna göre işlemler
    if game_state == "MENU":
        # Ana menü
        cv2.putText(img, "BALON TOPLAMA OYUNU", (screen_width // 2 - 150, screen_height // 2 - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Oyna butonu
        draw_button(img, play_button)
        
    elif game_state == "WAITING_FOR_HANDS":
        # Hedef daireleri çiz
        cv2.circle(img, right_target, target_radius, (0, 255, 0), 2)
        cv2.circle(img, left_target, target_radius, (0, 255, 0), 2)
        
        # Ellerin hedefe ulaşıp ulaşmadığını kontrol et
        right_in_position = False
        left_in_position = False
        
        if right_hand_position:
            right_distance = np.sqrt((right_hand_position[0] - right_target[0])**2 + 
                                    (right_hand_position[1] - right_target[1])**2)
            right_in_position = right_distance < target_radius
        
        if left_hand_position:
            left_distance = np.sqrt((left_hand_position[0] - left_target[0])**2 + 
                                   (left_hand_position[1] - left_target[1])**2)
            left_in_position = left_distance < target_radius
        
        # İki el de doğru pozisyonda ise geri sayıma başla
        if right_in_position and left_in_position:
            countdown_start = time.time()
            game_state = "COUNTDOWN"
        
        # Ekrana talimat yaz
        cv2.putText(img, "Elleri yesil dairelere yerlestirin", 
                   (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    elif game_state == "COUNTDOWN":
        # Hedef daireleri çiz
        cv2.circle(img, right_target, target_radius, (0, 255, 0), 2)
        cv2.circle(img, left_target, target_radius, (0, 255, 0), 2)
        
        # Geri sayım
        elapsed = time.time() - countdown_start
        countdown = 3 - int(elapsed)
        
        if countdown <= 0:
            game_state = "PLAYING"
            game_start_time = time.time()
            last_balloon_time = time.time()
        else:
            # Geri sayımı ekrana yaz
            cv2.putText(img, str(countdown), 
                       (screen_width // 2 - 20, screen_height // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 5)
    
    elif game_state == "PLAYING":
        # Kalan süreyi hesapla
        elapsed = time.time() - game_start_time
        remaining = max(0, game_duration - elapsed)
        
        # Oyun süresi doldu mu?
        if remaining <= 0:
            game_state = "GAME_OVER"
        
        # Yeni balon oluştur
        if time.time() - last_balloon_time > balloon_spawn_interval:
            balloons.append(Balloon(screen_width))
            last_balloon_time = time.time()
            balloon_spawn_interval = random.uniform(0.6, 1.2)  # Rastgele aralıklarla balon oluştur
        
        # İşaret parmağı ucuna kırmızı noktaları çiz
        if right_index_tip:
            # İşaret parmağı ucuna iki kırmızı nokta çiz (toplama noktaları)
            cv2.circle(img, right_index_tip, 10, (0, 0, 255), -1)  # Ana kırmızı nokta
            cv2.circle(img, (right_index_tip[0], right_index_tip[1] - 15), 6, (0, 0, 255), -1)  # Üstteki küçük kırmızı nokta
        
        if left_index_tip:
            # İşaret parmağı ucuna iki kırmızı nokta çiz (toplama noktaları)
            cv2.circle(img, left_index_tip, 10, (0, 0, 255), -1)  # Ana kırmızı nokta
            cv2.circle(img, (left_index_tip[0], left_index_tip[1] - 15), 6, (0, 0, 255), -1)  # Üstteki küçük kırmızı nokta
        
        # Balonları güncelle ve çiz
        for balloon in balloons[:]:
            balloon.update()
            
            # Balon ekrandan çıktı mı?
            if balloon.y > screen_height + balloon.size//2:
                balloons.remove(balloon)
                continue
            
            # Balon toplandı mı?
            if right_hand_found and right_index_tip and balloon.is_collected(right_index_tip[0], right_index_tip[1], "right"):
                score += 1
                balloons.remove(balloon)
                continue
            
            if left_hand_found and left_index_tip and balloon.is_collected(left_index_tip[0], left_index_tip[1], "left"):
                score += 1
                balloons.remove(balloon)
                continue
            
            balloon.draw(img)
        
        # Skoru ve kalan süreyi göster
        cv2.putText(img, f"Skor: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Sure: {int(remaining)}", (screen_width - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                   
        # Ekranın ortasına bir çizgi çiz
        cv2.line(img, (screen_width // 2, 0), (screen_width // 2, screen_height), 
                (255, 255, 255), 1)
        
        # Duraklatma butonu
        draw_button(img, pause_button)
        
    elif game_state == "PAUSED":
        # Duraklatma ekranı
        cv2.putText(img, "OYUN DURAKLATILDI", (screen_width // 2 - 150, screen_height // 2 - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Butonları çiz
        draw_button(img, resume_button)
        draw_button(img, restart_button)
        draw_button(img, menu_button)
        
    elif game_state == "GAME_OVER":
        # Oyun sonu ekranı
        cv2.putText(img, "OYUN BITTI", (screen_width // 2 - 150, screen_height // 2 - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        cv2.putText(img, f"Toplam Skor: {score}", (screen_width // 2 - 100, screen_height // 2 + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Butonları çiz
        draw_button(img, restart_button)
        draw_button(img, menu_button)
    
    # Sonucu göster
    cv2.imshow("Balon Toplama Oyunu", img)
    
    # Sadece çıkış için klavye kontrolü (isteğe bağlı)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
hands.close()
cap.release()
cv2.destroyAllWindows()
