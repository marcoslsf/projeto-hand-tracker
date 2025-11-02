import cv2
import mediapipe as mp
from hand_detector import HandTracker
import pyautogui
import tkinter as tk
from tkinter import messagebox
import threading
import time
import numpy as np

class AppController:
    def __init__(self):
        self.tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)
        self.last_fist_time = 0
        self.fist_hold_duration = 3.0  # segundos que a mão precisa ficar fechada
        self.fist_detected = False
        self.confirmation_shown = False
        
        # Controle do mouse
        self.mouse_mode = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.last_click_time = 0
        self.click_cooldown = 1.0  # segundos entre cliques
        
        # Suavização do movimento (filtro de média móvel exponencial)
        self.smooth_x = None
        self.smooth_y = None
        self.smoothing_factor = 0.85  # 0.0 = sem suavização, 1.0 = máximo (valores maiores = mais suave)
        
        # Sensibilidade - área da câmera que será usada (em porcentagem, 1.0 = 100%)
        # Valores menores = maior sensibilidade (menos movimento necessário)
        self.camera_area_ratio = 0.6  # usa 60% da área central da câmera
        
        # Inverter eixo Y se necessário (True = inverte Y)
        self.invert_y = False
        
    def show_confirmation(self):
        """Mostra modal de confirmação"""
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal
        root.attributes('-topmost', True)  # Mantém no topo
        
        result = messagebox.askyesno(
            "Confirmar Fechamento",
            "Deseja realmente fechar o aplicativo em foco?",
            parent=root
        )
        
        root.destroy()
        return result
    
    def close_active_app(self):
        """Fecha o app em foco usando Alt+F4"""
        pyautogui.hotkey('alt', 'f4')
    
    def is_fist_closed(self, landmarks):
        """Verifica se a mão está fechada usando a função do HandTracker"""
        tips = [8, 12, 16, 20]  # Pontas dos dedos
        pips = [6, 10, 14, 18]   # Articulações médias
        
        for tip_id, pip_id in zip(tips, pips):
            if landmarks[tip_id].y < landmarks[pip_id].y:
                return False
        return True
    
    def is_pinch_gesture(self, landmarks):
        """Verifica se polegar e indicador estão juntos (pinça) - move mouse"""
        thumb_tip = (landmarks[4].x, landmarks[4].y)
        index_tip = (landmarks[8].x, landmarks[8].y)
        distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5
        return distance < 0.03
    
    def is_hand_open(self, landmarks):
        """Verifica se todos os dedos estão estendidos (mão aberta) - clique"""
        # Pontas dos dedos: indicador(8), médio(12), anelar(16), mindinho(20)
        # Articulações médias: indicador(6), médio(10), anelar(14), mindinho(18)
        
        index_extended = landmarks[8].y < landmarks[6].y
        middle_extended = landmarks[12].y < landmarks[10].y
        ring_extended = landmarks[16].y < landmarks[14].y
        pinky_extended = landmarks[20].y < landmarks[18].y
        
        return index_extended and middle_extended and ring_extended and pinky_extended
    
    def move_mouse(self, x, y, frame_width, frame_height):
        """Move o mouse baseado na posição do dedo indicador com suavização"""
        # Define a área de trabalho na câmera (área central para maior sensibilidade)
        area_offset_x = frame_width * (1 - self.camera_area_ratio) / 2
        area_offset_y = frame_height * (1 - self.camera_area_ratio) / 2
        area_width = frame_width * self.camera_area_ratio
        area_height = frame_height * self.camera_area_ratio
        
        # Normaliza a posição para a área de trabalho (0 a 1)
        norm_x = (x - area_offset_x) / area_width if area_width > 0 else 0.5
        norm_y = (y - area_offset_y) / area_height if area_height > 0 else 0.5
        
        # Limita os valores entre 0 e 1
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Inverte Y se necessário
        if self.invert_y:
            norm_y = 1 - norm_y
        
        # Converte para coordenadas da tela
        target_x = norm_x * self.screen_width
        target_y = norm_y * self.screen_height
        
        # Aplica suavização (filtro de média móvel exponencial)
        if self.smooth_x is None or self.smooth_y is None:
            self.smooth_x = target_x
            self.smooth_y = target_y
        else:
            self.smooth_x = self.smooth_x * self.smoothing_factor + target_x * (1 - self.smoothing_factor)
            self.smooth_y = self.smooth_y * self.smoothing_factor + target_y * (1 - self.smoothing_factor)
        
        # Move o mouse suavemente (duration maior = movimento mais suave)
        pyautogui.moveTo(int(self.smooth_x), int(self.smooth_y), duration=0.15)
    
    def run(self):
        """Loop principal com tela de debug"""
        print("aplicativo rodando...")
        print("gestos disponiveis:")
        print("  - pinça (polegar e indicador juntos): move o mouse")
        print("  - mao aberta (todos dedos estendidos): clica")
        print("  - mao fechada: fecha app em foco (com confirmacao)")
        print("pressione ESC para sair")
        
        # Cria janela de debug
        cv2.namedWindow("Debug - Hand Landmarks", cv2.WINDOW_NORMAL)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)  # Espelha a imagem
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.tracker.hands.process(rgb)
            
            # Prepara frame de debug
            debug_frame = frame.copy()
            
            # Informações de status
            status_text = []
            status_text.append("status: aguardando mao")
            status_text.append("")
            
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    # Desenha landmarks e conexões
                    self.tracker.mp_draw.draw_landmarks(
                        debug_frame,
                        hand_landmarks,
                        self.tracker.mp_hands.HAND_CONNECTIONS,
                        self.tracker.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                        self.tracker.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )
                    
                    landmarks = hand_landmarks.landmark
                    h, w = frame.shape[:2]
                    
                    # Verifica gestos
                    is_fist = self.is_fist_closed(landmarks)
                    is_pinch = self.is_pinch_gesture(landmarks)
                    is_open = self.is_hand_open(landmarks)
                    
                    # Controle do mouse (pinça)
                    if is_pinch and not is_fist:
                        self.mouse_mode = True
                        # Usa o ponto médio entre polegar e indicador
                        thumb_tip = landmarks[4]
                        index_tip = landmarks[8]
                        mid_x = (thumb_tip.x + index_tip.x) / 2
                        mid_y = (thumb_tip.y + index_tip.y) / 2
                        
                        mouse_x = int(mid_x * w)
                        mouse_y = int(mid_y * h)
                        
                        # Move o mouse
                        self.move_mouse(mouse_x, mouse_y, w, h)
                        
                        # Desenha círculo no ponto médio da pinça
                        cv2.circle(debug_frame, (mouse_x, mouse_y), 15, (255, 0, 255), 3)
                        
                        status_text[0] = "status: controle do mouse ativo (pinça)"
                        status_text.append("abra a mao para clicar")
                    else:
                        self.mouse_mode = False
                        # Reseta suavização quando sai do modo mouse
                        self.smooth_x = None
                        self.smooth_y = None
                    
                    # Clique (mão aberta)
                    if is_open and not is_fist and not is_pinch:
                        current_time = time.time()
                        if current_time - self.last_click_time >= self.click_cooldown:
                            pyautogui.click()
                            self.last_click_time = current_time
                            status_text[0] = "status: clique realizado!"
                            status_text.append("mao aberta detectada")
                        else:
                            status_text[0] = "status: mao aberta (aguarde)"
                            status_text.append("cooldown do clique")
                    
                    # Fechar app (mão fechada)
                    if is_fist:
                        current_time = time.time()
                        
                        if not self.fist_detected:
                            self.last_fist_time = current_time
                            self.fist_detected = True
                        
                        hold_time = current_time - self.last_fist_time
                        remaining_time = self.fist_hold_duration - hold_time
                        
                        if remaining_time > 0:
                            status_text[0] = f"status: mao fechada ({remaining_time:.1f}s)"
                            status_text.append("aguarde para confirmar fechamento")
                        else:
                            status_text[0] = "status: pronto para fechar!"
                            status_text.append("modal aparecera em breve")
                        
                        # Verifica se a mão está fechada por tempo suficiente
                        if hold_time >= self.fist_hold_duration:
                            if not self.confirmation_shown:
                                self.confirmation_shown = True
                                
                                # Mostra confirmação em thread separada para não bloquear
                                def show_and_close():
                                    if self.show_confirmation():
                                        self.close_active_app()
                                    # Reseta após 2 segundos
                                    time.sleep(2)
                                    self.confirmation_shown = False
                                
                                thread = threading.Thread(target=show_and_close)
                                thread.daemon = True
                                thread.start()
                    elif not is_pinch and not is_open:
                        # Status padrão quando mão detectada mas sem gestos específicos
                        if not status_text or status_text[0] == "status: aguardando mao":
                            status_text[0] = "status: mao detectada"
                            status_text.append("pinça: move mouse | mao aberta: clique")
                        self.fist_detected = False
                        self.confirmation_shown = False
            
            # Desenha textos de status
            y_offset = 30
            for i, text in enumerate(status_text):
                cv2.putText(
                    debug_frame,
                    text,
                    (10, y_offset + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0) if "fechada" in text or "pronto" in text else (255, 255, 255),
                    2
                )
            
            # Mostra frame de debug
            cv2.imshow("Debug - Hand Landmarks", debug_frame)
            
            # Verifica se ESC foi pressionado
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

def main():
    controller = AppController()
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nsaindo...")
    finally:
        controller.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
