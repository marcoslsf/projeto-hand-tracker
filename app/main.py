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
        self.fist_hold_duration = 0.2  # segundos que a mão precisa ficar fechada
        self.fist_detected = False
        self.confirmation_shown = False
        
        # Controle do mouse
        self.mouse_mode = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.last_click_time = 0
        self.click_cooldown = 0.5  # segundos entre cliques
        
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
    
    def is_index_pointing(self, landmarks):
        """Verifica se apenas o dedo indicador está estendido (modo mouse)"""
        # Pontas dos dedos: polegar(4), indicador(8), médio(12), anelar(16), mindinho(20)
        # Articulações médias: indicador(6), médio(10), anelar(14), mindinho(18)
        
        # Indicador deve estar estendido
        index_extended = landmarks[8].y < landmarks[6].y
        
        # Outros dedos devem estar fechados
        middle_closed = landmarks[12].y > landmarks[10].y
        ring_closed = landmarks[16].y > landmarks[14].y
        pinky_closed = landmarks[20].y > landmarks[18].y
        
        return index_extended and middle_closed and ring_closed and pinky_closed
    
    def is_click_gesture(self, landmarks):
        """Verifica se polegar e indicador estão juntos (clique)"""
        thumb_tip = (landmarks[4].x, landmarks[4].y)
        index_tip = (landmarks[8].x, landmarks[8].y)
        distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5
        return distance < 0.03
    
    def move_mouse(self, x, y, frame_width, frame_height):
        """Move o mouse baseado na posição do dedo indicador"""
        # Converte coordenadas relativas para absolutas da tela
        screen_x = np.interp(x, [0, frame_width], [0, self.screen_width])
        screen_y = np.interp(y, [0, frame_height], [0, self.screen_height])
        
        # Inverte Y (a câmera está espelhada, mas a tela não)
        screen_y = self.screen_height - screen_y
        
        pyautogui.moveTo(int(screen_x), int(screen_y), duration=0.01)
    
    def run(self):
        """Loop principal com tela de debug"""
        print("aplicativo rodando...")
        print("gestos disponiveis:")
        print("  - dedo indicador estendido: move o mouse")
        print("  - juntar polegar e indicador: clica")
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
                    is_pointing = self.is_index_pointing(landmarks)
                    is_click = self.is_click_gesture(landmarks)
                    
                    # Controle do mouse (indicador apontando)
                    if is_pointing and not is_fist:
                        self.mouse_mode = True
                        index_tip = landmarks[8]
                        index_x = int(index_tip.x * w)
                        index_y = int(index_tip.y * h)
                        
                        # Move o mouse
                        self.move_mouse(index_x, index_y, w, h)
                        
                        # Desenha círculo no dedo indicador
                        cv2.circle(debug_frame, (index_x, index_y), 15, (255, 0, 255), 3)
                        
                        status_text[0] = "status: controle do mouse ativo"
                        
                        # Clique quando polegar e indicador se tocam
                        if is_click:
                            current_time = time.time()
                            if current_time - self.last_click_time >= self.click_cooldown:
                                pyautogui.click()
                                self.last_click_time = current_time
                                status_text.append("clique realizado!")
                            else:
                                status_text.append("aguarde para proximo clique")
                        else:
                            status_text.append("junte polegar e indicador para clicar")
                    else:
                        self.mouse_mode = False
                    
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
                    elif not is_pointing:
                        status_text[0] = "status: mao aberta"
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
