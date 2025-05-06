import pygame as pg
import numpy as np
import math
import random

# Konstanten
WIDTH, HEIGHT = 800, 600
HALF_HEIGHT = HEIGHT // 2
FOV = math.pi / 3.0  # 60 Grad Sichtfeld für realistischere Darstellung
HALF_FOV = FOV / 2  # 30 Grad nach links und rechts
NUM_RAYS = WIDTH    # Ein Strahl pro Pixel Breite
DEPTH = 20000       # Sehr große Sichtweite
SPEED = 2.5         # Bewegungsgeschwindigkeit

# KONSTANTEN FÜR 3D-RENDERING
RENDERING_ALWAYS_SHOW_ENEMIES = False  # Gegner werden NICHT durch Wände angezeigt
RENDERING_ALWAYS_SHOW_BULLETS = False  # Kugeln werden NICHT durch Wände angezeigt
RENDERING_DEBUG_MODE = False  # Debug-Ausgaben deaktiviert für bessere Performance
ENEMY_MIN_SIZE = 40  # Garantierte Mindestgröße für Gegner
ENEMY_BASE_SIZE_FACTOR = 2.0  # Grundgröße der Gegner relativ zur normalen Größe
BULLET_MIN_SIZE = 10  # Garantierte Mindestgröße für Kugeln
BULLET_BASE_SIZE_FACTOR = 1.5  # Grundgröße der Kugeln relativ zur normalen Größe
BULLET_TRAIL_LENGTH = 8.0  # Länge des Schweifs hinter Kugeln (Multiplikator der Größe)
ROT_SPEED = 0.025  # Langsamere Drehung für präziseres Zielen
INVERT_ANGLES = True  # WICHTIG: Diese Konstante sorgt dafür, dass alle Gegner korrekt bewegt werden

# Spieler-Position und Blickrichtung
player_x, player_y = 5, 5
player_angle = 0
player_health = 100
player_ammo = 50
player_score = 0

# Schussobjekte
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.2
        self.lifetime = 200  # DEUTLICH erhöhte Lebensdauer
        self.active = True
        self.hit_wall = False  # Flag für Wandkollision
        self.hit_pos_x = 0  # Position der Wandkollision
        self.hit_pos_y = 0
        self.hit_frames = 30  # Frames, die die Kugel nach Wandtreffer noch sichtbar bleibt
    
    def update(self):
        if not self.active:
            return False
        
        # Wenn Kugel eine Wand getroffen hat, zeige sie noch für eine Weile
        if self.hit_wall:
            self.hit_frames -= 1
            if self.hit_frames <= 0:
                self.active = False
                return False
            return True  # Kugel bleibt aktiv, aber bewegt sich nicht mehr
        
        # Normale Lebensdauer verringern
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            return False
        
        next_x = self.x + math.cos(self.angle) * self.speed
        next_y = self.y + math.sin(self.angle) * self.speed
        
        # Kollision mit Wänden - Kugel bleibt an der Wand sichtbar
        if game_map[int(next_y)][int(next_x)] > 0:
            self.hit_wall = True
            self.hit_pos_x = self.x  # Speichere die letzte Position vor dem Wandtreffer
            self.hit_pos_y = self.y
            # Debug-Ausgabe nur bei seltenen Gelegenheiten
            if random.random() < 0.1:  # Nur 10% aller Treffer werden geloggt
                print(f"Kugel trifft Wand bei ({self.x:.1f}, {self.y:.1f})")
            return True  # Kugel bleibt aktiv
        
        # Kollision mit Gegnern
        for enemy in enemies:
            if enemy.active and math.sqrt((enemy.x - next_x)**2 + (enemy.y - next_y)**2) < 0.5:
                enemy.health -= 25
                # Treffer-Meldung mit Namen des Gegners
                print(f"{enemy.name} wurde getroffen! Verbleibende Gesundheit: {enemy.health}")
                
                if enemy.health <= 0:
                    enemy.active = False
                    global player_score
                    player_score += 100
                    # Todes-Meldung
                    print(f"{enemy.name} wurde besiegt!")
                
                # Kugel bleibt kurz sichtbar bei Treffer
                self.hit_wall = True
                self.hit_pos_x = self.x
                self.hit_pos_y = self.y
                return True
        
        self.x, self.y = next_x, next_y
        return True

# Gegner
class Enemy:
    # Liste der möglichen Namen für Gegner
    ENEMY_NAMES = [
        "Hugo", "Brutus", "Zombie", "Drax", "Ghoul", "Phantom", "Wraith", 
        "Shadow", "Stalker", "Reaper", "Prowler", "Hunter", "Lurker", "Fiend",
        "Specter", "Demon", "Beast", "Menace", "Terror", "Fury", "Scourge",
        "Banshee", "Ghast", "Doom", "Phantom", "Torment", "Agony", "Sorrow",
        "Horror", "Dread", "Nachtmahr", "Geist", "Schatten", "Wüterich", "Berserker"
    ]
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.02  # Höhere Geschwindigkeit für bessere Sichtbarkeit der Bewegung
        self.health = 50
        self.active = True
        self.attack_cooldown = 180  # 3 Sekunden Cooldown zu Beginn
        self.attack_damage = 3  # Noch weniger Schaden
        self.min_attack_distance = 1.0  # Muss noch näher sein für Angriff
        
        # Eindeutiger Name für jeden Gegner
        self.name = random.choice(Enemy.ENEMY_NAMES)
        
        # Zusätzliche Bewegungsparameter für besseres Verhalten
        
        # Sofort ein Ziel setzen für bessere Bewegung
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(1.5, 3.0)
        self.target_x = x + math.cos(angle) * distance
        self.target_y = y + math.sin(angle) * distance
        
        # Sicherstellen, dass das Ziel innerhalb der Karte liegt
        self.target_x = max(1.0, min(MAP_SIZE-2.0, self.target_x))
        self.target_y = max(1.0, min(MAP_SIZE-2.0, self.target_y))
        
        # Sofort mit Patrouille beginnen für mehr Bewegung
        self.movement_state = "patrol"  # idle, patrol, chase, retreat
        self.state_timer = random.randint(120, 240)  # Längerer Timer für Anfangsbewegung
        self.path_timer = random.randint(180, 300)  # Wie lange der aktuelle Pfad verfolgt wird
        
        print(f"Gegner '{self.name}' erstellt bei ({x:.1f}, {y:.1f}), Ziel: ({self.target_x:.1f}, {self.target_y:.1f})")
        
        # Deutlich sichtbare Farbe und Größe 
        self.color = (random.randint(200, 255), random.randint(0, 50), random.randint(0, 50))
        self.size_multiplier = random.uniform(1.0, 1.3)  # Etwas unterschiedliche Größen
        
        # Angle-Offset für leichte Richtungsvariationen beibehalten
        self.angle_offset = random.uniform(-0.1, 0.1)
        
        # Debug-Infos für bessere Verfolgung
        print(f"Neuer Gegner '{self.name}' bei ({self.x:.1f}, {self.y:.1f})")
    
    def update(self):
        if not self.active:
            return
            
        # Abstand zum Spieler berechnen
        dx = player_x - self.x
        dy = player_y - self.y
        dist_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Timer für Zustandswechsel aktualisieren
        self.state_timer -= 1
        self.path_timer -= 1
        
        # ZUSTANDSBASIERTE KI-LOGIK
        # Zustandswechsel basierend auf Timer oder Spielerabstand
        if self.state_timer <= 0:
            # Zeit für einen möglichen Zustandswechsel
            if self.movement_state == "idle":
                # Nach Idle entweder patrouillieren oder verfolgen
                if dist_to_player < 5.0:  # Spieler in der Nähe, direkt verfolgen
                    self.movement_state = "chase"
                    self.path_timer = random.randint(180, 300)  # Längere Verfolgung
                else:
                    # Beginne zufällige Patrouille
                    self.movement_state = "patrol"
                    self.path_timer = random.randint(120, 240)
                    # Wähle zufälligen Patrouillienpunkt in der Nähe
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(2.0, 4.0)  # Kurze Patrouillendistanz
                    self.target_x = self.x + math.cos(angle) * distance
                    self.target_y = self.y + math.sin(angle) * distance
                    # Stelle sicher, dass der Zielpunkt innerhalb der Karte liegt
                    self.target_x = max(1.0, min(MAP_SIZE-2.0, self.target_x))
                    self.target_y = max(1.0, min(MAP_SIZE-2.0, self.target_y))
                    
            elif self.movement_state == "patrol":
                # Nach Patrouille entweder zurück zu Idle oder verfolgen
                if dist_to_player < 4.0:  # Spieler gesichtet
                    self.movement_state = "chase"
                    self.path_timer = random.randint(180, 300)
                    print(f"Gegner '{self.name}' bei ({self.x:.1f}, {self.y:.1f}) hat Spieler entdeckt")
                else:
                    # Zurück zu Idle für kurze Pause
                    self.movement_state = "idle"
                    self.state_timer = random.randint(60, 120)  # Kurze Pause
                    
            elif self.movement_state == "chase":
                # Nach Verfolgung entweder zurückziehen oder weiter verfolgen
                if dist_to_player > 8.0:  # Spieler zu weit weg, verliert Interesse
                    if random.random() < 0.7:  # 70% Chance auf Rückzug
                        self.movement_state = "retreat"
                        self.path_timer = random.randint(60, 120)
                        # Ziel ist aktueller Standort (Ausruhen)
                        self.target_x = self.x
                        self.target_y = self.y
                    else:  # 30% Chance weiter zu verfolgen
                        self.path_timer = random.randint(120, 180)
                elif dist_to_player < 1.0:  # Spieler sehr nah, manchmal zurückziehen
                    if random.random() < 0.3:  # 30% Chance auf taktischen Rückzug
                        self.movement_state = "retreat"
                        self.path_timer = random.randint(30, 60)  # Kurzer Rückzug
                        # Fluchtrichtung ist weg vom Spieler
                        retreat_angle = math.atan2(-dy, -dx)
                        retreat_dist = random.uniform(1.5, 3.0)
                        self.target_x = self.x + math.cos(retreat_angle) * retreat_dist
                        self.target_y = self.y + math.sin(retreat_angle) * retreat_dist
                        # Stelle sicher, dass der Zielpunkt innerhalb der Karte liegt
                        self.target_x = max(1.0, min(MAP_SIZE-2.0, self.target_x))
                        self.target_y = max(1.0, min(MAP_SIZE-2.0, self.target_y))
                else:  # Fortsetzung der Verfolgung
                    self.path_timer = random.randint(120, 240)
                
            elif self.movement_state == "retreat":
                # Nach Rückzug immer zu Idle
                self.movement_state = "idle"
                self.state_timer = random.randint(60, 120)  # Pause nach Rückzug
            
            # Timer zurücksetzen
            self.state_timer = random.randint(180, 300)  # 3-5 Sekunden
            # Debug-Ausgaben mit Namen des Gegners
            if random.random() < 0.001:  # Nur 0.1% der Zustandswechsel werden geloggt
                print(f"Gegner '{self.name}' bei ({self.x:.1f}, {self.y:.1f}) wechselt zu Zustand: {self.movement_state}")
        
        # BEWEGUNGSBERECHNUNG basierend auf aktuellem Zustand
        move_dir_x = 0
        move_dir_y = 0
        
        if self.movement_state == "idle":
            # Im Idle-Zustand minimale zufällige Bewegung
            move_dir_x = random.uniform(-0.1, 0.1)
            move_dir_y = random.uniform(-0.1, 0.1)
            move_speed = self.speed * 0.2  # Sehr langsam im Idle
            
        elif self.movement_state == "patrol":
            # Zum Patrouillenziel bewegen
            target_dx = self.target_x - self.x
            target_dy = self.target_y - self.y
            target_dist = math.sqrt(target_dx*target_dx + target_dy*target_dy)
            
            if target_dist < 0.2:  # Ziel erreicht
                # Neues Patrouillenziel wählen - direkt hier um schneller zu reagieren
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(1.5, 3.0)
                self.target_x = self.x + math.cos(angle) * distance
                self.target_y = self.y + math.sin(angle) * distance
                # Sicherstellen, dass das Ziel innerhalb der Karte liegt
                self.target_x = max(1.0, min(MAP_SIZE-2.0, self.target_x))
                self.target_y = max(1.0, min(MAP_SIZE-2.0, self.target_y))
                
                # Extrem reduzierte Debug-Ausgaben für bessere Performance
                if random.random() < 0.001:  # Nur 0.1% der Zielerreichungen werden geloggt
                    print(f"Gegner '{self.name}' bei ({self.x:.1f}, {self.y:.1f}) hat Ziel erreicht, neues Ziel: ({self.target_x:.1f}, {self.target_y:.1f})")
                
                # Timers zurücksetzen mit kürzerer Dauer für häufigere Aktionen
                self.path_timer = random.randint(90, 180)
                self.state_timer = random.randint(60, 120)
            else:
                # Zum Ziel bewegen
                move_dir_x = target_dx / target_dist
                move_dir_y = target_dy / target_dist
                
            # Schnellere Geschwindigkeit für bessere Sichtbarkeit
            move_speed = self.speed * 1.0  # Volle Geschwindigkeit
            
        elif self.movement_state == "chase":
            # Spieler direkt verfolgen aber mit leichtem Ausweichverhalten
            # für realistischere Bewegung
            # WICHTIG: dx und dy sind bereits relativ zur Spielerposition berechnet
            # (dx = player_x - self.x und dy = player_y - self.y)
            # Daher führt diese Bewegung direkt zum Spieler, unabhängig vom Spielerblickwinkel
            move_dir_x = dx
            move_dir_y = dy
            
            # Geschwindigkeit je nach Entfernung anpassen - SCHNELLER für bessere Sichtbarkeit
            if dist_to_player > 6:
                move_speed = self.speed * 2.0  # Deutlich schneller wenn weit weg
            elif dist_to_player < 1.5:
                move_speed = self.speed * 0.8  # Langsamer wenn nah dran, aber nicht zu langsam
            else:
                move_speed = self.speed * 1.5  # Generell schneller
                
        elif self.movement_state == "retreat":
            # Zum Rückzugsziel bewegen
            target_dx = self.target_x - self.x
            target_dy = self.target_y - self.y
            target_dist = math.sqrt(target_dx*target_dx + target_dy*target_dy)
            
            if target_dist < 0.2:  # Ziel erreicht
                self.path_timer = 0  # Erzwingt Zustandswechsel
            else:
                # Zum Ziel bewegen
                move_dir_x = target_dx / target_dist
                move_dir_y = target_dy / target_dist
            
            # Schneller zurückziehen
            move_speed = self.speed * 1.2
        
        # KOLLISIONSVERMEIDUNG zwischen Gegnern
        for other in enemies:
            if other != self and other.active:
                other_dx = other.x - self.x
                other_dy = other.y - self.y
                other_dist = math.sqrt(other_dx*other_dx + other_dy*other_dy)
                
                # Stärkeres Ausweichen für natürlichere Gruppenbewegung
                if other_dist < 1.2:  # Größerer Ausweichradius
                    avoid_strength = max(0, (1.2 - other_dist)) * 1.5  # Stärkere Abstoßung
                    move_dir_x -= other_dx / other_dist * avoid_strength
                    move_dir_y -= other_dy / other_dist * avoid_strength
        
        # BEWEGUNGSANWENDUNG und KOLLISIONSPRÜFUNG
        # Normalisieren des Bewegungsvektors
        move_length = math.sqrt(move_dir_x*move_dir_x + move_dir_y*move_dir_y)
        if move_length > 0.0001:  # Verhindere Division durch Null
            # Normalisieren
            move_dir_x /= move_length
            move_dir_y /= move_length
            
            # Leichte Zufallsbewegung für natürlicheres Verhalten
            jitter = 0.1  # Kleiner Zufallsfaktor
            move_dir_x += random.uniform(-jitter, jitter)
            move_dir_y += random.uniform(-jitter, jitter)
            
            # Renormalisieren nach Zufallskomponente
            move_length = math.sqrt(move_dir_x*move_dir_x + move_dir_y*move_dir_y)
            if move_length > 0.0001:
                move_dir_x /= move_length
                move_dir_y /= move_length
            
            # HIER WAR DER FEHLER: Move-Speed war zu klein
            # Erhöhe die Bewegungsgeschwindigkeit für sichtbare Bewegung
            move_speed = max(move_speed, 0.02)  # Garantierte Mindestgeschwindigkeit
            
            # Neue Position berechnen - ABSOLUT IN WELTKOORDINATEN!
            # Wichtig: Diese Position ist unabhängig vom Spielerwinkel und Kamerablick
            next_x = self.x + move_dir_x * move_speed
            next_y = self.y + move_dir_y * move_speed
            
            # DEBUGGING: Zeige gelegentlich die absoluten Weltkoordinaten der Gegner an
            if random.random() < 0.001:  # 0.1% Chance pro Frame
                print(f"Gegner '{self.name}' absolute Weltposition: ({self.x:.2f}, {self.y:.2f}) -> " +
                      f"Nächste Position: ({next_x:.2f}, {next_y:.2f}), " +
                      f"Unabhängig vom Spielerwinkel: {player_angle:.2f}")
            
            # Bewegungsvektoren gelegentlich anzeigen
            if random.random() < 0.0005:  # 0.05% Chance pro Frame
                print(f"Gegner '{self.name}' bei ({self.x:.2f}, {self.y:.2f}) bewegt sich: dx={move_dir_x:.2f}, dy={move_dir_y:.2f}, " +
                      f"speed={move_speed:.4f}")
                if self.movement_state == "patrol":
                    print(f"  Patrouilliert zu Ziel: ({self.target_x:.2f}, {self.target_y:.2f})")
            
            # Kollisionsprüfung mit Karte und Grenzen
            if 1 < next_x < MAP_SIZE-2 and 1 < next_y < MAP_SIZE-2:
                # Separate Prüfung für X und Y ermöglicht Gleiten entlang von Wänden
                # Prüfe Y-Bewegung
                if game_map[int(next_y)][int(self.x)] == 0:
                    # Freier Weg, normal bewegen
                    self.y = next_y
                else:
                    # Y-Bewegung kollidiert - versuche leichte Korrektur
                    # Teste etwas nach oben oder unten
                    if next_y > self.y and game_map[int(self.y) + 1][int(self.x)] == 0:
                        # Nur einen kleinen Schritt in die richtige Richtung
                        self.y += 0.1
                    elif next_y < self.y and game_map[int(self.y) - 1][int(self.x)] == 0:
                        # Nur einen kleinen Schritt in die richtige Richtung
                        self.y -= 0.1
                
                # Prüfe X-Bewegung
                if game_map[int(self.y)][int(next_x)] == 0:
                    # Freier Weg, normal bewegen
                    self.x = next_x
                else:
                    # X-Bewegung kollidiert - versuche leichte Korrektur
                    # Teste etwas nach links oder rechts
                    if next_x > self.x and game_map[int(self.y)][int(self.x) + 1] == 0:
                        # Nur einen kleinen Schritt in die richtige Richtung
                        self.x += 0.1
                    elif next_x < self.x and game_map[int(self.y)][int(self.x) - 1] == 0:
                        # Nur einen kleinen Schritt in die richtige Richtung
                        self.x -= 0.1
                    
                # Bei Kollision neues Ziel suchen im Patrouillen-Modus
                if (self.x != next_x or self.y != next_y) and self.movement_state == "patrol":
                    self.path_timer = 0  # Erzwingt neue Zielsetzung
                    
                    # Extrem reduziertes Logging
                    if random.random() < 0.0005:  # Nur 0.05% der Kollisionen loggen
                        print(f"Gegner '{self.name}' kollidiert mit Wand bei ({self.x:.1f}, {self.y:.1f}), sucht neues Ziel")
            else:
                # Außerhalb der Karte, Ziel ändern
                if self.movement_state == "patrol" or self.movement_state == "retreat":
                    self.path_timer = 0  # Neues Ziel setzen
                    # Extrem reduziertes Logging
                    if random.random() < 0.0001:  # Nur 0.01% der Fälle loggen
                        print(f"Gegner '{self.name}' außerhalb der Karte bei ({self.x:.1f}, {self.y:.1f}), sucht neues Ziel")
        
        # SPIELER-INTERAKTION (Angriff)
        # Angriff nur wenn im Verfolgungs-Modus, nah am Spieler und Cooldown abgelaufen
        if self.movement_state == "chase" and dist_to_player < self.min_attack_distance and self.attack_cooldown <= 0:
            global player_health
            player_health -= self.attack_damage
            self.attack_cooldown = 60  # 1 Sekunde zwischen Angriffen
            # Angemessene Debug-Ausgabe für Angriffe
            if random.random() < 0.1:  # 10% der Angriffe werden geloggt
                print(f"Gegner '{self.name}' greift an! Schaden: {self.attack_damage}, Spieler hat noch {player_health} Leben")
                # Zeige Entfernung zum Spieler für bessere Diagnose
                print(f"  Abstand zum Spieler: {dist_to_player:.2f}, Position: ({self.x:.2f}, {self.y:.2f})")
        
        # Cooldown-Timer aktualisieren
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

# Karte (0 = freier Platz, 1 = Wand)
MAP_SIZE = 10
game_map = np.zeros((MAP_SIZE, MAP_SIZE), dtype=int)
game_map[0, :] = 1  # Obere Wand
game_map[:, 0] = 1  # Linke Wand
game_map[MAP_SIZE-1, :] = 1  # Untere Wand
game_map[:, MAP_SIZE-1] = 1  # Rechte Wand
game_map[5, 5] = 1  # Ein Hindernis in der Mitte

# Gegner und Projektile
enemies = []
bullets = []

# Schusssound
shoot_sound = None

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKGRAY = (60, 60, 60)
YELLOW = (255, 255, 0)

# Hilfsfunktion für Winkelberechnungen
def normalize_angle(angle):
    """Normalisiert einen Winkel auf den Bereich [-π, π]"""
    while angle < -math.pi:
        angle += 2 * math.pi
    while angle > math.pi:
        angle -= 2 * math.pi
    return angle

def compute_screen_x(world_x, world_y, player_x, player_y, player_angle, fov, screen_width):
    """
    Berechnet die X-Position auf dem Bildschirm für ein Objekt in Weltkoordinaten.
    
    Diese Funktion implementiert den Kernalgorithmus der perspektivischen Projektion
    und wird für das Debugging verwendet, um die korrekte Projektion zu überprüfen.
    
    Parameter:
    - world_x, world_y: Position des Objekts in der Welt
    - player_x, player_y: Position des Spielers
    - player_angle: Blickwinkel des Spielers (in Radiant)
    - fov: Field of View (in Radiant)
    - screen_width: Breite des Bildschirms in Pixeln
    
    Rückgabe:
    - Die X-Koordinate auf dem Bildschirm
    - Der relative Winkel zwischen Spielerblickrichtung und Objekt
    """
    # 1. Relative Position
    dx = world_x - player_x
    dy = world_y - player_y
    
    # 2. Absoluter Winkel vom Spieler zum Objekt
    abs_angle = math.atan2(dy, dx)
    
    # 3. Relativer Winkel zum Spielerblickfeld
    rel_angle = normalize_angle(abs_angle - player_angle)
    
    # KORREKTUR: Vorzeichen IMMER umkehren für korrekte Bewegungsrichtung
    # Bei Blickrichtungsänderung muss sich die Position der Objekte entsprechend ändern
    # Die Invertierung muss für ALLE Objekte angewendet werden!
    rel_angle = -rel_angle
    
    # Zusätzliche Winkelkorrektur für Randfälle
    # Dies ist wichtig für Gegner, die sich in Grenzbereichen des Sichtfelds befinden
    if rel_angle < -math.pi:
        rel_angle += 2 * math.pi
    elif rel_angle > math.pi:
        rel_angle -= 2 * math.pi
    
    # 4. X-Position auf dem Bildschirm
    # Verbesserte Formel mit Begrenzung auf den sichtbaren Bildschirmbereich
    screen_x = (0.5 - rel_angle / fov) * screen_width
    screen_x = min(screen_width, max(0, screen_x))  # Sicherstellung valider Werte
    
    return screen_x, rel_angle


def cast_ray(angle):
    """
    Erweiterte Version des Raycasting-Algorithmus mit größerer Sichtdistanz
    und verbesserter Leistung.
    """
    # Richtungsvektor des Strahls
    ray_dir_x = math.cos(angle)
    ray_dir_y = math.sin(angle)
    
    # Aktuelle Map-Zelle des Spielers
    map_x, map_y = int(player_x), int(player_y)
    
    # Länge von ray von einer x oder y Seite zur nächsten x oder y Seite
    delta_dist_x = float('inf') if ray_dir_x == 0 else abs(1 / ray_dir_x)
    delta_dist_y = float('inf') if ray_dir_y == 0 else abs(1 / ray_dir_y)
    
    # Schrittrichtung in x oder y und Entfernung zum nächsten x oder y
    if ray_dir_x < 0:
        step_x = -1
        side_dist_x = (player_x - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - player_x) * delta_dist_x
    
    if ray_dir_y < 0:
        step_y = -1
        side_dist_y = (player_y - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - player_y) * delta_dist_y
    
    # DDA Algorithmus mit Verbesserungen
    hit = 0
    side = 0  # x = 0, y = 1
    max_steps = 500  # EXTREM erhöhte maximale Anzahl von Schritten für enorme Sichtweite!
    steps = 0
    
    # Schleife mit erhöhter maximaler Schrittanzahl
    while hit == 0 and steps < max_steps:
        # Nächster Schritt in X oder Y-Richtung
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        
        steps += 1
        
        # Prüfen ob außerhalb der Karte (betrachte dies als einen "Hit" am Rand des Universums)
        if not (0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE):
            return DEPTH, side  # Strahl geht ins Nirgendwo
        
        # Prüfen ob Strahl eine Wand getroffen hat
        if game_map[map_y][map_x] > 0:
            hit = 1
    
    # Wenn kein Treffer gefunden wurde, gib maximale Entfernung zurück
    if hit == 0:
        return DEPTH, side
    
    # Berechne die exakte Entfernung zur getroffenen Wand
    if side == 0:  # X-Seite getroffen
        wall_dist = (map_x - player_x + (1 - step_x) / 2) / ray_dir_x
    else:  # Y-Seite getroffen
        wall_dist = (map_y - player_y + (1 - step_y) / 2) / ray_dir_y
    
    # Distanz begrenzen auf vernünftige Werte
    wall_dist = min(wall_dist, DEPTH)
    
    return wall_dist, side


def draw_3d_view(screen):
    """3D-Ansicht mit Raycasting - KOMPLETT ÜBERARBEITETER ALGORITHMUS"""
    # RESET: Fülle den Bildschirm mit Himmel und Boden
    screen.fill(DARKGRAY, (0, 0, WIDTH, HALF_HEIGHT))  # Himmel
    screen.fill(BLACK, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))  # Boden
    
    # GRUNDLAGE: Speichern der Distanzen für die Gegneranzeige und Z-Buffer
    z_buffer = [float('inf')] * NUM_RAYS  # Mit Unendlich initialisieren
    
    # DEBUGGING: Zeige Spielerposition und Blickrichtung für bessere Fehlerdiagnose
    if pg.time.get_ticks() % 180 == 0:  # Alle 3 Sekunden
        print(f"SPIELER: Position=({player_x:.2f}, {player_y:.2f}), " + 
              f"Blickwinkel={player_angle:.2f} rad = {math.degrees(player_angle):.1f}°, " +
              f"FOV={FOV:.2f} rad = {math.degrees(FOV):.1f}°")
    
    # WÄNDE: Einfache Farben für Wände
    wall_colors = [
        (200, 200, 200),  # Weiß
        (150, 150, 150),  # Grau (dunklere Seite)
    ]
    
    # SCHRITT 1: ALLE WÄNDE RENDERN - Wichtig für korrekte Z-Buffer-Werte
    for x in range(NUM_RAYS):
        # Berechne den Winkel des aktuellen Strahls
        ray_angle = player_angle - HALF_FOV + FOV * x / NUM_RAYS
        
        # Cast Ray und erhalte Entfernung
        distance, side = cast_ray(ray_angle)
        
        # Speichern für Z-Buffer (tatsächliche Entfernung, nicht korrigiert)
        z_buffer[x] = distance
        
        # Korrigiere Fisheye-Effekt für Rendering
        corrected_dist = distance * math.cos(player_angle - ray_angle)
        
        # Berechne Höhe der zu zeichnenden Linie
        line_height = min(int(HEIGHT / corrected_dist), HEIGHT) if corrected_dist > 0 else HEIGHT
        
        # Startpunkt der Linie
        line_start = HALF_HEIGHT - line_height // 2
        
        # Wandfarbe (dunkler, wenn Seite = 1)
        color = wall_colors[side]
        
        # Entfernungsschatten
        shade = max(0.3, min(1.0, 1.0 / (1 + distance * 0.1)))
        color = (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade))
        
        # Zeichne vertikale Linie
        pg.draw.line(screen, color, (x, line_start), (x, line_start + line_height), 1)
    
    # SCHRITT 2: ALLE SPRITES SAMMELN (Gegner und Schüsse)
    sprites_to_render = []
    
    # MÄSSIG HÄUFIGE DEBUGGING-INFORMATION (ALLE 5 SEKUNDEN)
    if pg.time.get_ticks() % 300 == 0 and random.random() < 0.5:  # 50% Chance alle 5 Sekunden
        active_enemies = [e for e in enemies if e.active]
        print("================================")
        print(f"SPIELER: ({player_x:.2f}, {player_y:.2f}), Winkel: {math.degrees(player_angle):.1f}°")
        print(f"GEGNER: {len(active_enemies)} aktiv")
        # Nur die ersten 2 Gegner anzeigen, um Spam zu reduzieren
        for i, e in enumerate(active_enemies[:2]):
            print(f"  {i+1}. ({e.x:.2f}, {e.y:.2f}), Zustand: {e.movement_state}")
        if len(active_enemies) > 2:
            print(f"  ... und {len(active_enemies)-2} weitere Gegner")
        print("================================")
    
    # SCHRITT 2A: GEGNER-SPRITES SAMMELN
    # Extra Debug-Ausgabe, wenn Debug-Modus aktiv ist
    if RENDERING_DEBUG_MODE and pg.time.get_ticks() % 180 == 0:
        print("\n=== GEGNER-SPRITE-SAMMLUNG START ===")
        print(f"Spielerposition: ({player_x:.2f}, {player_y:.2f}), Blickwinkel: {math.degrees(player_angle):.1f}°")
    
    for enemy in enemies:
        if not enemy.active:
            continue
        
        # SCHRITT 1: RELATIVE POSITION BERECHNEN
        # Vektor vom Spieler zum Gegner (in Weltkoordinaten)
        dx = enemy.x - player_x
        dy = enemy.y - player_y
        
        # SCHRITT 2: DISTANZ BERECHNEN
        # Euklidischer Abstand für korrekte Distanz
        dist = math.sqrt(dx*dx + dy*dy)
        
        # SCHRITT 3: WINKEL BERECHNEN 
        # Absoluter Winkel in der Welt (vom Spieler zum Gegner)
        absolute_angle_to_enemy = math.atan2(dy, dx)
        
        # SCHRITT 4: RELATIVER WINKEL ZUR KAMERA
        # KERNPROBLEM GELÖST: Korrekte Berechnung des relativen Winkels
        # Bei Drehung nach rechts müssen Objekte nach links wandern und umgekehrt
        relative_angle = normalize_angle(absolute_angle_to_enemy - player_angle)
        
        # WICHTIG: Das Vorzeichen sollte NICHT pauschal invertiert werden, da dies
        # nur in bestimmten Winkelbereichen korrekt funktioniert.
        # Wir lassen es jetzt unverändert für konsistente Darstellung.
        
        # Zusätzliche Normalisierung für Grenzfälle (wichtig bei Winkeln nahe ±π)
        if relative_angle < -math.pi:
            relative_angle += 2 * math.pi
        elif relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        
        # Debug-Ausgabe im Debug-Modus für jeden 10. Gegner (wenn aktiviert)
        if RENDERING_DEBUG_MODE and random.random() < 0.05:  # Auf 5% reduziert
            print(f"Gegner ID={id(enemy)}: Weltpos=({enemy.x:.2f}, {enemy.y:.2f})")
            print(f"  Relativ zum Spieler: dx={dx:.2f}, dy={dy:.2f}, Dist={dist:.2f}")
            print(f"  Absoluter Winkel: {math.degrees(absolute_angle_to_enemy):.1f}°")
            print(f"  Relativer Winkel zur Kamera: {math.degrees(relative_angle):.1f}°")
        
        # SCHRITT 5: GEGNER ZUR RENDERING-LISTE HINZUFÜGEN
        sprites_to_render.append({
            'type': 'enemy',
            'obj': enemy,
            'dist': dist,           # Für Sortierung und Skalierung
            'dx': dx,               # Relative X-Position vom Spieler
            'dy': dy,               # Relative Y-Position vom Spieler
            'world_x': enemy.x,     # Absolute X-Position in der Welt
            'world_y': enemy.y,     # Absolute Y-Position in der Welt
            'abs_angle': absolute_angle_to_enemy,  # Winkel in Weltkoordinaten
            'rel_angle': relative_angle            # Winkel relativ zur Kamera
        })
    
    # Abschließende Debug-Ausgabe
    if RENDERING_DEBUG_MODE and pg.time.get_ticks() % 180 == 0:
        print(f"Gesammelte Gegner: {len([s for s in sprites_to_render if s['type'] == 'enemy'])}")
        print("=== GEGNER-SPRITE-SAMMLUNG ENDE ===\n")
        
        # SELTENES LOGGING ZUR FEHLERSUCHE (nur für 2% der Gegner)
        if random.random() < 0.02:
            print(f"Gegner an ({enemy.x:.2f}, {enemy.y:.2f}) - " +
                  f"Relativ zum Spieler: ({dx:.2f}, {dy:.2f}), " +
                  f"Winkel: {math.degrees(absolute_angle_to_enemy):.1f}°, " +
                  f"Relativ zur Blickrichtung: {math.degrees(relative_angle):.1f}°")
        # Diese Debug-Info entfernen, da 'dist' hier noch nicht definiert ist
        # und wir bereits bessere Debug-Ausgaben haben
    
    # SCHRITT 2B: PROJEKTILE/SCHÜSSE SAMMELN
    # Debug-Information, wenn Debug-Modus aktiv
    if RENDERING_DEBUG_MODE and pg.time.get_ticks() % 180 == 0:
        print("\n=== PROJEKTIL-SPRITE-SAMMLUNG START ===")
        print(f"Aktive Projektile: {len([b for b in bullets if b.active])}")
    
    for bullet in bullets:
        if not bullet.active:
            continue
        
        # SCHRITT 1: WELTPOSITION BESTIMMEN
        # Bei Wandtreffern die Trefferposition verwenden, sonst aktuelle Position
        bullet_world_x = bullet.hit_pos_x if bullet.hit_wall else bullet.x
        bullet_world_y = bullet.hit_pos_y if bullet.hit_wall else bullet.y
        
        # SCHRITT 2: RELATIVE POSITION BERECHNEN
        # Vektor vom Spieler zum Projektil
        dx = bullet_world_x - player_x
        dy = bullet_world_y - player_y
        
        # SCHRITT 3: DISTANZ BERECHNEN
        # Für korrekte Größenskalierung und Z-Buffer
        dist = math.sqrt(dx*dx + dy*dy)
        
        # SCHRITT 4: WINKEL BERECHNEN
        # Absoluter Winkel in der Welt (vom Spieler zum Projektil)
        absolute_angle_to_bullet = math.atan2(dy, dx)
        
        # SCHRITT 5: RELATIVER WINKEL ZUR KAMERA
        # KERNPROBLEM GELÖST: Korrekte Berechnung des relativen Winkels
        # Bei Drehung nach rechts müssen Objekte nach links wandern
        relative_angle = normalize_angle(absolute_angle_to_bullet - player_angle)
        
        # WICHTIG: Das Vorzeichen sollte wie bei den Gegnern behandelt werden
        # für eine konsistente Darstellung aller Objekte in der 3D-Ansicht.
        
        # Zusätzliche Normalisierung für Grenzfälle (wichtig bei Winkeln nahe ±π)
        if relative_angle < -math.pi:
            relative_angle += 2 * math.pi
        elif relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        
        # Debug-Ausgabe für einzelne Projektile (reduziert für bessere Performance)
        if RENDERING_DEBUG_MODE and random.random() < 0.02:  # Auf 2% reduziert
            print(f"Projektil: Weltpos=({bullet_world_x:.2f}, {bullet_world_y:.2f})")
            print(f"  Rel. zum Spieler: dx={dx:.2f}, dy={dy:.2f}, Dist={dist:.2f}")
            print(f"  Abs. Winkel: {math.degrees(absolute_angle_to_bullet):.1f}°")
            print(f"  Rel. Winkel: {math.degrees(relative_angle):.1f}°")
            print(f"  Status: {'Wandtreffer' if bullet.hit_wall else 'In Bewegung'}")
        
        # SCHRITT 6: PROJEKTIL ZUR RENDERING-LISTE HINZUFÜGEN
        sprites_to_render.append({
            'type': 'bullet',
            'obj': bullet,
            'dist': dist,          # Für Sortierung und Z-Buffer
            'dx': dx,              # Relative X-Position
            'dy': dy,              # Relative Y-Position
            'world_x': bullet_world_x,  # Absolute X-Position
            'world_y': bullet_world_y,  # Absolute Y-Position
            'abs_angle': absolute_angle_to_bullet,  # Absoluter Winkel
            'rel_angle': relative_angle,            # Relativer Winkel zur Kamera
            'hit_wall': bullet.hit_wall,            # Für Spezialeffekte
            'hit_frames': bullet.hit_frames         # Für Animation
        })
    
    # Abschließende Debug-Ausgabe
    if RENDERING_DEBUG_MODE and pg.time.get_ticks() % 180 == 0:
        print(f"Gesammelte Projektile: {len([s for s in sprites_to_render if s['type'] == 'bullet'])}")
        print("=== PROJEKTIL-SPRITE-SAMMLUNG ENDE ===\n")
        
        # Optimierungshinweis: Wir haben redundante Debug-Ausgaben entfernt und 
        # durch den zentralen Debug-Modus ersetzt
    
    # SORTIEREN DER SPRITES: Wichtig, damit entfernte zuerst gezeichnet werden (Painter's Algorithm)
    sprites_to_render.sort(key=lambda sprite: sprite['dist'], reverse=True)
    
    # UMFASSENDE DEBUGGING-STATISTIK (praktisch deaktiviert)
    if RENDERING_DEBUG_MODE and pg.time.get_ticks() % 3000 == 0 and random.random() < 0.01:  # Nur 1% alle 50 Sekunden
        print("\n======= SPRITE-RENDERING-STATISTIK =======")
        print(f"Spieler: Position=({player_x:.2f}, {player_y:.2f}), Blickwinkel={math.degrees(player_angle):.1f}°")
        print(f"Sichtfeld (FOV): {math.degrees(FOV):.1f}° ({math.degrees(HALF_FOV):.1f}° in jede Richtung)")
        print(f"Sprites gesamt: {len(sprites_to_render)}")
        print(f"  - Gegner: {len([s for s in sprites_to_render if s['type'] == 'enemy'])}")
        print(f"  - Projektile: {len([s for s in sprites_to_render if s['type'] == 'bullet'])}")
        print("===========================================\n")
    
    # ZÄHLER FÜR STATISTIK
    sprites_seen = 0        # Gesamtzahl der gerenderten Sprites
    sprites_in_fov = 0      # Sprites im Sichtfeld (nicht am Rand)
    
    # SCHRITT 3: SPRITE-RENDERING
    for sprite in sprites_to_render:
        # SCHRITT 3.1: DIREKTES VERWENDEN DER VORBERECHNETEN WERTE
        # Wir nutzen die vorberechneten Werte statt neue Berechnungen durchzuführen
        dist = sprite['dist']
        relative_angle = sprite['rel_angle']  # Geändert von relative_angle zu rel_angle
        
        # VEREINFACHTE BERECHNUNG: Keine spezielle Behandlung mehr basierend auf der Entfernung
        # Wir verwenden direkt die berechneten Werte und entfernen die unnötige Neuberechnung
        if sprite['type'] == 'enemy':
            # Verwende direkt die bereits berechneten Werte aus dem Sprite-Objekt
            dx = sprite['dx'] 
            dy = sprite['dy']
            dist = sprite['dist']  # Nutze gespeicherte Distanz
            
            # Wir verwenden den bereits berechneten relativen Winkel ohne Änderung
            # Das vermeidet Inkonsistenzen zwischen verschiedenen Bereichen des Codes
            relative_angle = sprite['rel_angle']
        
        # KERNALGORITHMUS DER PERSPEKTIVISCHEN PROJEKTION
        
        # SCHRITT 3.2: BILDSCHIRMPOSITION BERECHNEN
        #
        # Dies ist DIE kritische Formel für die korrekte Positionierung
        # Wir bilden den Winkelbereich [-FOV/2, FOV/2] auf den Bildschirm [0, WIDTH] ab
        # Die Mitte des Bildschirms (WIDTH/2) entspricht einem relativen Winkel von 0
        # Negative Winkel sind links, positive rechts von der Mitte
        #
        # KORRIGIERTER FIX:
        # 1. Zusätzliche Normalisierung für Grenzbereiche
        if relative_angle < -math.pi:
            relative_angle += 2 * math.pi
        elif relative_angle > math.pi:
            relative_angle -= 2 * math.pi
            
        # NEUE VERBESSERTE FORMEL:
        # Hier liegt der Schlüssel zur korrekten Darstellung
        # Das Mapping zwischen relativem Winkel und Bildschirmposition muss konsistent sein:
        # - Objekte links vom Spieler (negative Winkel) müssen rechts auf dem Bildschirm erscheinen
        # - Objekte rechts vom Spieler (positive Winkel) müssen links auf dem Bildschirm erscheinen
        sprite_screen_x = (0.5 + relative_angle / FOV) * WIDTH
        
        # SEHR DETAILLIERTES DEBUGGING für Gegner (extrem reduziert)
        if RENDERING_DEBUG_MODE and random.random() < 0.0001 and sprite['type'] == 'enemy':  # Auf 0.01% reduziert
            enemy = sprite['obj']
            print("\n=== DETAILLIERTE PROJEKTION (GEGNER) ===")
            print(f"ID: {id(enemy)}, Position: ({enemy.x:.2f}, {enemy.y:.2f})")
            print(f"Spieler: ({player_x:.2f}, {player_y:.2f}), Blick: {math.degrees(player_angle):.1f}°")
            print(f"Relativer Winkel: {math.degrees(relative_angle):.2f}°")
            print(f"Projektion: 0.5 - {relative_angle:.4f}/{FOV:.4f} = {0.5 - relative_angle/FOV:.4f}")
            print(f"Bildschirmposition: {sprite_screen_x:.1f} von {WIDTH} Pixeln")
            if abs(relative_angle) > HALF_FOV:
                print(f"HINWEIS: Objekt außerhalb des Sichtfelds (HALF_FOV={math.degrees(HALF_FOV):.1f}°)")
            print("==========================================\n")
        
        # SCHRITT 3.3: SICHTBARKEIT BESTIMMEN UND SCREEN_X FESTLEGEN
        margin = 30  # Mindestabstand vom Bildschirmrand (in Pixeln)
        
        # Prüfen, ob das Objekt innerhalb des strengen Sichtfelds liegt
        # KORRIGIERT: Nur Gegner im tatsächlichen Sichtfeld anzeigen
        if abs(relative_angle) < HALF_FOV:  # Nur im exakten FOV anzeigen
            # Position aus korrigierter Projektion übernehmen
            screen_x = int(min(WIDTH - margin, max(margin, sprite_screen_x)))
            sprites_in_fov += 1  # Statistik: Im Sichtfeld
            
            # Flag setzen, dass der Gegner sichtbar ist
            sprite['is_visible'] = True
        else:
            # Außerhalb des Sichtfelds - NICHT anzeigen
            sprite['is_visible'] = False
            # Position außerhalb des Bildschirms setzen (wird später kontrolliert)
            screen_x = -1000
        
        # Statistik: Sprite wurde verarbeitet
        sprites_seen += 1
        
        # DEBUG: Zusammenfassung der finalen Position (nur wenn Debug-Modus aktiv)
        if RENDERING_DEBUG_MODE and random.random() < 0.001 and sprite['type'] == 'enemy':  # Stark reduziert
            enemy = sprite['obj']
            in_fov_text = "IM SICHTFELD" if abs(relative_angle) < HALF_FOV else "AUSSERHALB SICHTFELD"
            print(f"POSITION: Gegner bei ({enemy.x:.1f}, {enemy.y:.1f}) -> Screen-X: {screen_x}")
            print(f"  Dist: {dist:.1f}, Status: {in_fov_text}, Winkel: {math.degrees(relative_angle):.1f}°")
            
        # Größe des Sprites basierend auf Entfernung
        sprite_size = int(min(HEIGHT, WIDTH / 2) / (dist + 0.0001))
        
        # Platziere Sprite vertikal in der Mitte des Bildschirms
        sprite_top = HALF_HEIGHT - sprite_size // 2
        
        # Wenn es ein Gegner ist
        if sprite['type'] == 'enemy':
            enemy = sprite['obj']
            
            # Überprüfen, ob der Gegner sichtbar ist - wenn nicht, überspringen
            if not sprite.get('is_visible', False):
                continue
            
            # ABSOLUTE MEGA-SICHTBARKEIT: Gegner sind immer gut zu sehen
            # In allen Entfernungen gut sichtbar mit Mindestgröße
            
            # Größere Basisgröße für bessere Sichtbarkeit
            base_size = int(sprite_size * ENEMY_BASE_SIZE_FACTOR)
            
            # GROSSZÜGIGE Mindestgröße garantieren, egal wie weit entfernt
            # Nutze die globale Konstante für einheitliche Größe
            min_size = ENEMY_MIN_SIZE
            
            # Spezialformel für Entfernungsskalierung:
            # 1. Nah: Normal groß
            # 2. Mittel: Leichte Abnahme
            # 3. Fern: Konstante Mindestgröße
            dist_factor = 1.0
            if dist > 0:
                # SEHR LANGSAME Verkleinerung mit zunehmender Entfernung
                dist_factor = max(0.9, 15.0 / (dist + 8.0))
                
                # Bonus für extrem weit entfernte Gegner (damit sie nicht verschwinden)
                if dist > 20:
                    dist_factor = max(dist_factor, 0.9)
            
            # Gesamtgröße berechnen und auf Minimum prüfen
            # Nutze die Individuelle Größenmultiplikation des Gegners
            calc_size = int(base_size * dist_factor * enemy.size_multiplier)
            # NIEMALS unter die Mindestgröße fallen
            final_size = max(min_size, calc_size)
            
            # Position im Bildschirm wird IMMER genutzt
            # Wir haben bereits sichergestellt, dass screen_x innerhalb der Bildschirmgrenzen liegt
            # Gegner IMMER sichtbar machen, komplett unabhängig von Wänden
            # Aber mit Unterscheidung zwischen Gegnern vor und hinter Wänden
            ray_pos = min(WIDTH-1, max(0, screen_x))  # Begrenze auf Bildschirmgrenzen
            
            # Prüfen ob der Gegner hinter einer Wand ist
            # Die Z-Buffer-Distanz an dieser Stelle gibt die Wandentfernung an
            wall_dist = z_buffer[ray_pos]
            behind_wall = (dist > wall_dist)
            
            # STARKER FARBUNTERSCHIED für Sichtbarkeit hinter Wänden
            if behind_wall and RENDERING_ALWAYS_SHOW_ENEMIES:
                # X-RAY SICHT: Gegner hinter Wand mit speziellem Effekt
                
                # 1. Blauer Farbton für "durch Wand sichtbar"-Effekt
                enemy_color = (50, 50, 255)  # Kräftiges Blau für Gegner hinter Wänden
                
                # 2. LEUCHTENDE Kontur für maximale Sichtbarkeit hinter Wänden
                # Größerer Kontur-Umriss
                outline_size = max(2, final_size // 6)
                
                # Äußere Kontur (cyan/türkis) für Kontrast
                pg.draw.rect(screen, (0, 255, 255), 
                           (screen_x - final_size//2 - outline_size, 
                            sprite_top + final_size//4 - outline_size, 
                            final_size + outline_size*2, 
                            final_size + outline_size*2), 
                            outline_size)
                            
                # Zweite innere Kontur (weiß) für noch besseren Kontrast
                inner_outline = max(1, outline_size // 2)
                pg.draw.rect(screen, (200, 200, 255), 
                           (screen_x - final_size//2 - inner_outline, 
                            sprite_top + final_size//4 - inner_outline, 
                            final_size + inner_outline*2, 
                            final_size + inner_outline*2), 
                            inner_outline)
            else:
                # Gegner im Vordergrund: Leuchtend rot
                enemy_color = (255, 0, 0)  # Reines Rot
                
            # Verbesserte Debug-Info für bessere Fehlerdiagnose
            if pg.time.get_ticks() % 300 == 0 and random.random() < 0.05:  # 5% Chance alle 5 Sekunden
                print(f"Gegner '{enemy.name}' erscheint bei ({enemy.x:.1f}, {enemy.y:.1f}), "
                      f"Abstand zum Spieler: {dist:.1f}, "
                      f"Zustand: {enemy.movement_state}")
                
                # Zusätzliche Debug-Info für bestimmte Gegner
                if random.random() < 0.2:  # Nur für 20% der Debug-Ausgaben
                    print(f"Gegner '{enemy.name}' absolute Weltposition: "
                          f"({enemy.x:.2f}, {enemy.y:.2f}) -> "
                          f"Bildschirmposition: {screen_x:.2f}, "
                          f"Unabhängig vom Spielerwinkel: {player_angle:.2f}")
            
            # VIEL GRÖSSERER Körper für bessere Sichtbarkeit
            # Grundform: Rechteck
            pg.draw.rect(screen, enemy_color, 
                       (screen_x - final_size//2, sprite_top + final_size//4, 
                       final_size, final_size))
            
            # Kopf: Deutlich größerer Kreis
            pg.draw.circle(screen, enemy_color, 
                          (screen_x, sprite_top + final_size//5), 
                          int(final_size * 0.4))  # Größerer Kopf: 40% der Gesamtgröße
                
            # ULTRA-AUFFÄLLIGE AUGEN für perfekte Sichtbarkeit
            eye_spacing = final_size // 5
            
            # Äußerer Glow-Effekt für die Augen (leicht pulsierend)
            pulse = (math.sin(pg.time.get_ticks() / 150) * 0.2 + 0.8)  # 0.6 bis 1.0
            glow_size = max(4, int(final_size * 0.25 * pulse))
            
            # Leuchtender Glow um die Augen herum - weiße Aura
            pg.draw.circle(screen, (255, 255, 255, 180),  # Halbtransparentes Weiß
                         (screen_x - eye_spacing, sprite_top + final_size//5), 
                         glow_size)
            pg.draw.circle(screen, (255, 255, 255, 180),  # Halbtransparentes Weiß
                         (screen_x + eye_spacing, sprite_top + final_size//5), 
                         glow_size)
            
            # Große, leuchtende Augen - intensiver Kontrast 
            eye_size = max(4, int(final_size * 0.15))
            
            # Extra Kontur um die Augen (schwarz)
            outline = max(1, int(eye_size * 0.2))
            pg.draw.circle(screen, (0, 0, 0),  # Schwarz
                         (screen_x - eye_spacing, sprite_top + final_size//5), 
                         eye_size + outline)
            pg.draw.circle(screen, (0, 0, 0),  # Schwarz
                         (screen_x + eye_spacing, sprite_top + final_size//5), 
                         eye_size + outline)
            
            # Eigentliche Augen - extraleuchtendes Gelb
            pg.draw.circle(screen, (255, 255, 0),  # Gelb
                         (screen_x - eye_spacing, sprite_top + final_size//5), 
                         eye_size)
            pg.draw.circle(screen, (255, 255, 0),  # Gelb
                         (screen_x + eye_spacing, sprite_top + final_size//5), 
                         eye_size)
            
            # Große, leuchtend rote Pupillen für dämonischen Effekt
            pupil_size = max(2, int(eye_size * 0.6))
            pg.draw.circle(screen, (255, 0, 0),  # Rot
                         (screen_x - eye_spacing, sprite_top + final_size//5), 
                         pupil_size)
            pg.draw.circle(screen, (255, 0, 0),  # Rot
                         (screen_x + eye_spacing, sprite_top + final_size//5), 
                         pupil_size)
                         
            # Innerster Glanzpunkt für 3D-Effekt (weißer Punkt)
            shine_size = max(1, int(pupil_size * 0.3))
            shine_offset = max(1, int(pupil_size * 0.2))
            pg.draw.circle(screen, (255, 255, 255),  # Weiß
                         (screen_x - eye_spacing - shine_offset, 
                          sprite_top + final_size//5 - shine_offset), 
                         shine_size)
            pg.draw.circle(screen, (255, 255, 255),  # Weiß
                         (screen_x + eye_spacing - shine_offset, 
                          sprite_top + final_size//5 - shine_offset), 
                         shine_size)
            
            # Normale, aber gut sichtbare Gesundheitsanzeige
            health_bar_height = max(3, int(final_size * 0.07))  # 7% der Gesamtgröße
            health_width = int(final_size * (enemy.health / 50))
            
            # Hintergrund (roter Balken)
            pg.draw.rect(screen, (150, 0, 0), 
                       (screen_x - final_size//2, sprite_top - health_bar_height*2, 
                        final_size, health_bar_height))
            
            # Vordergrund (grüner Balken)
            pg.draw.rect(screen, (0, 200, 0), 
                       (screen_x - final_size//2, sprite_top - health_bar_height*2, 
                        health_width, health_bar_height))
            
            # Dünner Rahmen für bessere Sichtbarkeit
            pg.draw.rect(screen, (255, 255, 255), 
                       (screen_x - final_size//2, sprite_top - health_bar_height*2, 
                        final_size, health_bar_height), 1)  # 1 Pixel Rand
            
            # VERBESSERTE Status-Anzeige mit verschiedenen Zuständen
            status_size = max(3, int(final_size * 0.08))  # 8% der Gesamtgröße
            
            # Unterschiedliche Farben basierend auf dem aktuellen Zustand
            if enemy.movement_state == "idle":
                # Grün = Idle/Ruhezustand (passive)
                status_color = (0, 200, 0)
            elif enemy.movement_state == "patrol":
                # Blau = Patrouille (neutral)
                status_color = (50, 100, 255)
            elif enemy.movement_state == "chase":
                # Rot = Verfolgung (aggressiv)
                status_color = (255, 50, 50)
            elif enemy.movement_state == "retreat":
                # Gelb = Rückzug (Flucht)
                status_color = (255, 255, 0)
            else:
                # Fallback für unbekannte Zustände
                status_color = (150, 150, 150)
                
            # Zeichne Statusindikator
            pg.draw.circle(screen, status_color, 
                          (screen_x, sprite_top - health_bar_height*3), status_size)
                          
            # Pulsierender Effekt für den Chase-Zustand
            if enemy.movement_state == "chase":
                # Extra pulsierender Ring für Verfolgungsmodus
                pulse = (math.sin(pg.time.get_ticks() / 120) * 0.5 + 0.5)  # 0.0 bis 1.0
                outer_size = status_size + int(status_size * pulse)
                pg.draw.circle(screen, (255, 100, 100, 150), 
                             (screen_x, sprite_top - health_bar_height*3), outer_size, 1)
        
        # Wenn es ein Schuss ist
        elif sprite['type'] == 'bullet':
            # Überprüfen, ob der Schuss sichtbar ist - wenn nicht, überspringen
            if not sprite.get('is_visible', False):
                continue
                
            # ULTIMATIV SICHTBARE KUGELN
            # Verwende die globalen Konstanten für konsistente Darstellung
            base_bullet_size = int(sprite_size * BULLET_BASE_SIZE_FACTOR)
            min_bullet_size = BULLET_MIN_SIZE
            
            # Spezielle Skalierung für perfekte Kugeldarstellung
            # Garantiert große Sichtbarkeit bis in extreme Entfernungen
            bullet_scale = 1.0
            if dist > 0:
                # Angepasste Formel für langsamere Größenabnahme
                bullet_scale = max(0.6, 4.0 / (dist + 0.5))
                
                # Bonus für weit entfernte Kugeln
                if dist > 10:
                    # Zusätzlicher Faktor, damit Kugeln in der Ferne nicht zu klein werden
                    far_bonus = 0.3 + (dist - 10) * 0.05  # +5% pro Einheit über 10
                    bullet_scale = max(bullet_scale, far_bonus)
                
            # Berechnete Größe mit absolutem Minimum
            calc_bullet_size = int(base_bullet_size * bullet_scale)
            bullet_size = max(min_bullet_size, calc_bullet_size)
            
            # BONUS: Pulsierende Größe für bessere Sichtbarkeit
            pulse = math.sin(pg.time.get_ticks() / 100) * 0.15 + 1.0  # 0.85 bis 1.15
            bullet_size = int(bullet_size * pulse)
            
            # Immer zeichnen, da screen_x bereits auf den sichtbaren Bildschirmbereich begrenzt wurde
            # Position auf dem Bildschirm
            bullet_y = HALF_HEIGHT
            
            # Angemessen reduzierte Debug-Ausgaben für bessere Verfolgung
            if pg.time.get_ticks() % 600 == 0 and random.random() < 0.01:  # 1% Chance alle 10 Sekunden
                print(f"Zeichne Schuss bei {screen_x},{bullet_y} | Größe={bullet_size}, Entfernung={dist:.1f}")
                
            # Prüfen ob die Kugel eine Wand getroffen hat
            hit_wall = sprite.get('hit_wall', False)
            hit_frames = sprite.get('hit_frames', 0)
            
            # Prüfen, ob die Kugel hinter einer Wand ist
            ray_pos = min(WIDTH-1, max(0, screen_x))
            bullet_behind_wall = (dist > z_buffer[ray_pos])
            
            # Spezielle Darstellung für Wandtreffer
            if hit_wall:
                # ULTRA-EXPLOSIVE Effekte bei Wandtreffer
                # Intensität der Explosion basierend auf verbleibenden Frames
                intensity = hit_frames / 30.0  # 0.0 bis 1.0
                
                # Größere Explosionsgröße für bessere Sichtbarkeit
                explosion_size = int(bullet_size * 3.0 * intensity)
                
                # EXTRA: Bei Kugeln hinter Wänden trotzdem sichtbar machen
                if bullet_behind_wall and RENDERING_ALWAYS_SHOW_BULLETS:
                    # Explosionskontur für bessere Sichtbarkeit hinter Wänden
                    outline_size = 3
                    pg.draw.circle(screen, (0, 200, 255), 
                                 (screen_x, bullet_y), 
                                 explosion_size + outline_size, outline_size)
                
                # 1. Äußerer Explosionskreis (intensiv gelb-orange-rot)
                # Stärkere Farben für bessere Sichtbarkeit
                pg.draw.circle(screen, (255, 100 + int(155 * intensity), 0), 
                             (screen_x, bullet_y), explosion_size)
                
                # 2. Mittlerer Explosionskreis (hell-orange bis gelb)
                mid_size = int(explosion_size * 0.7)  # Größerer mittlerer Kreis
                pg.draw.circle(screen, (255, 180 + int(75 * intensity), 0), 
                             (screen_x, bullet_y), mid_size)
                
                # 3. Kern der Explosion (weiß-gelb mit Pulsieren)
                # Pulsierender Kern für mehr visuelle Auffälligkeit
                pulse_factor = 0.8 + math.sin(pg.time.get_ticks() / 50) * 0.2  # 0.6 bis 1.0
                core_size = int(explosion_size * 0.4 * pulse_factor)
                pg.draw.circle(screen, (255, 255, 100), 
                             (screen_x, bullet_y), core_size)
                
                # Innerer leuchtender Punkt (weiß) für Kontrast
                pg.draw.circle(screen, (255, 255, 255), 
                             (screen_x, bullet_y), int(core_size * 0.3))
                
                # 4. MEHR Funkenstrahlen in ALLE Richtungen
                # Stärkerer visueller Effekt mit mehr Strahlen
                num_rays = int(16 * intensity)  # Mehr Strahlen!
                for i in range(num_rays):
                    # Zufälliger Winkel im 360°-Bereich für Rundumeffekt
                    ray_angle = random.uniform(0, 2 * math.pi)
                    
                    # Zufällige, längere Strahlen
                    ray_length = random.uniform(explosion_size * 0.5, explosion_size * 2.0)
                    
                    # Endpunkt berechnen
                    end_x = screen_x + math.cos(ray_angle) * ray_length
                    end_y = bullet_y + math.sin(ray_angle) * ray_length
                    
                    # Farbe basierend auf Intensität - verschiedene Farben für Effekt
                    if i % 3 == 0:
                        ray_color = (255, 200, 0)  # Gelb
                    elif i % 3 == 1:
                        ray_color = (255, 100, 0)  # Orange
                    else:
                        ray_color = (255, 255, 100)  # Helles Gelb
                        
                    # Dickere Strahlen für bessere Sichtbarkeit
                    pg.draw.line(screen, ray_color, 
                               (screen_x, bullet_y), (end_x, end_y), 
                               max(2, int(3 * intensity)))
            else:
                # ULTRA-AUFFÄLLIGE KUGEL in Bewegung
                
                # Spezielle Behandlung für Kugeln hinter Wänden
                if bullet_behind_wall and RENDERING_ALWAYS_SHOW_BULLETS:
                    # Blauer Randeffekt für Kugeln hinter Wänden
                    outline_size = 3
                    pg.draw.circle(screen, (0, 200, 255), 
                                 (screen_x, bullet_y), 
                                 bullet_size * 1.8, outline_size)
                
                # 1. Äußerer Leuchtkreis (hellgelb) - GRÖSSER und HELLER
                outer_size = bullet_size * 2.0
                pg.draw.circle(screen, (255, 255, 150), (screen_x, bullet_y), outer_size)
                
                # 2. Mittlerer Kreis (intensiv gelb)
                mid_size = bullet_size * 1.5
                pg.draw.circle(screen, (255, 255, 0), (screen_x, bullet_y), mid_size)
                
                # 3. Innerer Kern (weiß - strahlend hell)
                inner_size = bullet_size * 0.7
                pg.draw.circle(screen, (255, 255, 255), (screen_x, bullet_y), inner_size)
                
                # 4. EXTRA-LANGER Bewegungstrail für maximale Sichtbarkeit
                # Berechne Richtungsvektor
                angle = math.atan2(sprite['dy'], sprite['dx'])
                
                # Flugrichtung mit Streifen zeigen (entgegen der Bewegungsrichtung)
                reverse_angle = angle + math.pi
                
                # DEUTLICH längerer Trail für bessere Sichtbarkeit
                streak_length = bullet_size * BULLET_TRAIL_LENGTH
                end_x = screen_x + math.cos(reverse_angle) * streak_length
                end_y = bullet_y + math.sin(reverse_angle) * streak_length
                
                # MEHRERE Streifen für "Feuer"-Effekt
                
                # 1. Äußerer Streifen (gelb, breit, transparent)
                outer_streak_width = max(4, int(bullet_size * 0.9))
                pg.draw.line(screen, (255, 255, 0, 100), 
                           (screen_x, bullet_y), (end_x, end_y), outer_streak_width)
                
                # 2. Mittlerer Streifen (orange)
                mid_streak_width = max(3, int(bullet_size * 0.7))
                mid_streak_length = streak_length * 0.8
                mid_end_x = screen_x + math.cos(reverse_angle) * mid_streak_length
                mid_end_y = bullet_y + math.sin(reverse_angle) * mid_streak_length
                pg.draw.line(screen, (255, 200, 0, 150), 
                           (screen_x, bullet_y), (mid_end_x, mid_end_y), mid_streak_width)
                
                # 3. Innerer Streifen (weiß, intensiv)
                inner_streak_width = max(2, int(bullet_size * 0.4))
                inner_streak_length = streak_length * 0.5
                inner_end_x = screen_x + math.cos(reverse_angle) * inner_streak_length
                inner_end_y = bullet_y + math.sin(reverse_angle) * inner_streak_length
                pg.draw.line(screen, (255, 255, 255, 200), 
                           (screen_x, bullet_y), (inner_end_x, inner_end_y), inner_streak_width)
                           
                # 4. BONUS: Pulsierender Glow-Effekt um die Kugel
                pulse_time = pg.time.get_ticks() / 80
                glow_size = outer_size * (0.9 + math.sin(pulse_time) * 0.1)
                pg.draw.circle(screen, (255, 255, 200, 50), 
                             (screen_x, bullet_y), glow_size, 3)
    
    # Waffe zeichnen
    weapon_img_height = 200
    weapon_bounce = math.sin(pg.time.get_ticks() / 200) * 5  # Leichtes Wackeln
    weapon_pos = HEIGHT - weapon_img_height + weapon_bounce
    
    # Primitive Waffe zeichnen
    pg.draw.rect(screen, (100, 100, 100), (WIDTH//2 - 20, weapon_pos + 100, 40, 100))
    pg.draw.rect(screen, (80, 80, 80), (WIDTH//2 - 10, weapon_pos + 50, 20, 70))
    
    # Mündungsfeuer bei Schuss anzeigen
    if shooting_cooldown > 8:  # Nur kurz nach dem Schuss
        fire_size = random.randint(10, 20)
        pg.draw.circle(screen, YELLOW, (WIDTH//2, weapon_pos + 40), fire_size)
        pg.draw.circle(screen, (255, 150, 0), (WIDTH//2, weapon_pos + 40), fire_size - 5)
    
    # Fadenkreuz zeichnen
    pg.draw.line(screen, WHITE, (WIDTH//2 - 10, HEIGHT//2), (WIDTH//2 + 10, HEIGHT//2), 2)
    pg.draw.line(screen, WHITE, (WIDTH//2, HEIGHT//2 - 10), (WIDTH//2, HEIGHT//2 + 10), 2)


def draw_minimap(screen):
    """Minimap anzeigen - STARK verbessert für bessere Übersicht"""
    # GRÖSSERE Minimap für bessere Sichtbarkeit
    mini_size = 10  # Doppelt so große Kacheln für bessere Sicht
    map_width = MAP_SIZE * mini_size
    map_height = MAP_SIZE * mini_size
    
    # Halbtransparenter Hintergrund für bessere Lesbarkeit
    bg_surface = pg.Surface((map_width, map_height), pg.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))  # Schwarz mit 70% Transparenz
    screen.blit(bg_surface, (0, 0))
    
    # Gitternetz für bessere Orientierung
    for i in range(MAP_SIZE + 1):
        # Horizontale Linien
        pg.draw.line(screen, (100, 100, 100), 
                    (0, i * mini_size), 
                    (map_width, i * mini_size), 1)
        # Vertikale Linien
        pg.draw.line(screen, (100, 100, 100), 
                    (i * mini_size, 0), 
                    (i * mini_size, map_height), 1)
    
    # Karte zeichnen
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if game_map[y][x] > 0:  # Nur Wände zeichnen
                pg.draw.rect(screen, (200, 200, 200), 
                            (x * mini_size, y * mini_size, mini_size, mini_size))
    
    # LEGENDÄRE Sichtbare Linien zeichnen (Raycasting-Visualisierung)
    # Vereinfachte Strahlen für besseres Verständnis
    ray_count = 20  # Weniger Strahlen für die Minimap
    for i in range(ray_count):
        ray_angle = player_angle - HALF_FOV + FOV * i / ray_count
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)
        
        # Zeichne Sichtstrahl bis zur Wand oder Maximalentfernung
        max_dist = 10  # Maximale Distanz des Strahls
        for j in range(1, int(max_dist * 10)):
            check_x = player_x + ray_dir_x * j * 0.1
            check_y = player_y + ray_dir_y * j * 0.1
            
            # Prüfe ob außerhalb der Karte oder Wand getroffen
            if not (0 <= int(check_x) < MAP_SIZE and 0 <= int(check_y) < MAP_SIZE):
                break
            if game_map[int(check_y)][int(check_x)] > 0:
                break
            
            # Zeichne Punkt entlang des Strahls (semi-transparent)
            if j % 3 == 0:  # Nur jeden dritten Punkt für weniger Überladung
                pg.draw.circle(screen, (100, 255, 100, 150), 
                              (int(check_x * mini_size), int(check_y * mini_size)), 1)
    
    # Gegner auf der Karte zeichnen - VIEL größer und auffälliger
    for enemy in enemies:
        if enemy.active:
            # Unterschiedliche Farben je nach Zustand des Gegners
            if enemy.movement_state == "idle":
                enemy_color = (0, 200, 0)  # Grün im Ruhezustand
            elif enemy.movement_state == "patrol":
                enemy_color = (100, 100, 255)  # Blau bei Patrouille
            elif enemy.movement_state == "chase":
                enemy_color = (255, 0, 0)  # Rot bei Verfolgung
            elif enemy.movement_state == "retreat":
                enemy_color = (255, 255, 0)  # Gelb bei Rückzug
            else:
                enemy_color = (150, 150, 150)  # Grau für unbekannte Zustände
            
            # Pulsierender Effekt für bessere Sichtbarkeit
            # Stärkeres Pulsieren für aggressivere Zustände
            if enemy.movement_state == "chase":
                pulse = (math.sin(pg.time.get_ticks() / 120) * 0.7 + 1.8)  # 1.1 bis 2.5 (schneller, größer)
            else:
                pulse = (math.sin(pg.time.get_ticks() / 200) * 0.5 + 1.5)  # 1.0 bis 2.0 (normal)
                
            enemy_size = int(3 * pulse)
            
            # Gegner zeichnen
            pg.draw.circle(screen, enemy_color, 
                          (int(enemy.x * mini_size), int(enemy.y * mini_size)), 
                          enemy_size)
                          
            # Zusätzlich Bewegungsrichtungslinie für bessere Sichtbarkeit
            if enemy.movement_state in ["patrol", "chase", "retreat"]:
                # Berechne den Richtungsvektor
                if enemy.movement_state == "patrol" or enemy.movement_state == "retreat":
                    # Zum Ziel
                    dir_x = enemy.target_x - enemy.x
                    dir_y = enemy.target_y - enemy.y
                elif enemy.movement_state == "chase":
                    # Zum Spieler
                    dir_x = player_x - enemy.x
                    dir_y = player_y - enemy.y
                
                # Normalisiere und skaliere den Vektor
                dir_len = math.sqrt(dir_x*dir_x + dir_y*dir_y)
                if dir_len > 0.0001:
                    dir_x = dir_x / dir_len * enemy_size * 1.5
                    dir_y = dir_y / dir_len * enemy_size * 1.5
                    
                    # Zeichne Richtungslinie
                    pg.draw.line(screen, enemy_color,
                               (int(enemy.x * mini_size), int(enemy.y * mini_size)),
                               (int((enemy.x + dir_x) * mini_size), int((enemy.y + dir_y) * mini_size)),
                               max(1, int(enemy_size / 3)))
    
    # Projektile auf der Karte zeichnen - Größer mit Leuchteffekt
    for bullet in bullets:
        if bullet.active:
            if bullet.hit_wall:
                # Explosionseffekt auf der Minimap
                intensity = bullet.hit_frames / 30.0  # 0.0 bis 1.0
                explosion_size = int(5 * intensity)  # Größe der Explosion auf der Minimap
                
                # Hauptexplosion - orange
                pg.draw.circle(screen, (255, 150, 0), 
                              (int(bullet.hit_pos_x * mini_size), int(bullet.hit_pos_y * mini_size)), 
                              explosion_size)
                
                # Innere Explosion - helles Gelb
                inner_size = max(2, int(explosion_size * 0.6))
                pg.draw.circle(screen, (255, 255, 100), 
                              (int(bullet.hit_pos_x * mini_size), int(bullet.hit_pos_y * mini_size)), 
                              inner_size)
                
                # Zufällige Partikel um die Explosion
                particles = int(8 * intensity)
                for i in range(particles):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(explosion_size * 0.5, explosion_size * 2)
                    px = bullet.hit_pos_x + math.cos(angle) * (dist / mini_size)
                    py = bullet.hit_pos_y + math.sin(angle) * (dist / mini_size)
                    size = max(1, int(2 * intensity))
                    pg.draw.circle(screen, (255, 200, 0), 
                                  (int(px * mini_size), int(py * mini_size)), 
                                  size)
            else:
                # Bewegungsspur (kleine Punkte hinter dem Projektil)
                angle = bullet.angle + math.pi  # Umgekehrte Richtung
                for i in range(1, 10, 2):
                    trace_x = bullet.x - math.cos(angle) * (i * 0.1)
                    trace_y = bullet.y - math.sin(angle) * (i * 0.1)
                    trace_size = 3 - (i // 3)
                    pg.draw.circle(screen, (200, 200, 0), 
                                  (int(trace_x * mini_size), int(trace_y * mini_size)), 
                                  trace_size)
                
                # Hauptprojektil - gelb und größer
                pg.draw.circle(screen, (255, 255, 0), 
                              (int(bullet.x * mini_size), int(bullet.y * mini_size)), 
                              3)
    
    # Spieler auf der Karte zeichnen - Größer und auffälliger
    player_radius = 4
    # Hinterer Kreis (Schatten/Halo)
    pg.draw.circle(screen, (0, 100, 0), 
                  (int(player_x * mini_size), int(player_y * mini_size)), 
                  player_radius + 2)
    # Hauptkreis (Spieler)
    pg.draw.circle(screen, (0, 255, 0), 
                  (int(player_x * mini_size), int(player_y * mini_size)), 
                  player_radius)
    
    # Blickrichtung als Dreieck (intuitiver als Linie)
    direction_length = 8
    end_x = player_x + math.cos(player_angle) * direction_length / mini_size
    end_y = player_y + math.sin(player_angle) * direction_length / mini_size
    
    # Berechne die Eckpunkte des Dreiecks
    angle1 = player_angle + 0.3
    angle2 = player_angle - 0.3
    x1 = player_x + math.cos(angle1) * 0.5
    y1 = player_y + math.sin(angle1) * 0.5
    x2 = player_x + math.cos(angle2) * 0.5
    y2 = player_y + math.sin(angle2) * 0.5
    
    # Zeichne gefülltes Dreieck für die Richtung
    pg.draw.polygon(screen, (0, 255, 0), [
        (int(player_x * mini_size), int(player_y * mini_size)),
        (int(x1 * mini_size), int(y1 * mini_size)),
        (int(end_x * mini_size), int(end_y * mini_size)),
        (int(x2 * mini_size), int(y2 * mini_size))
    ])


def handle_movement(keys):
    """Spielerbewegung und Kollisionserkennung"""
    global player_x, player_y, player_angle
    
    # Bewegungsfaktor - noch etwas langsamer für bessere Kontrolle
    move_speed = 0.03
    
    # Drehen
    if keys[pg.K_LEFT]:
        player_angle -= ROT_SPEED
    if keys[pg.K_RIGHT]:
        player_angle += ROT_SPEED
    
    # Bewegungsrichtung
    dx = 0
    dy = 0
    
    # Vorwärts/Rückwärts
    if keys[pg.K_w] or keys[pg.K_UP]:
        dx += math.cos(player_angle) * SPEED
        dy += math.sin(player_angle) * SPEED
    
    if keys[pg.K_s] or keys[pg.K_DOWN]:
        dx -= math.cos(player_angle) * SPEED
        dy -= math.sin(player_angle) * SPEED
    
    # Seitliche Bewegung
    if keys[pg.K_a]:
        dx += math.sin(player_angle) * SPEED
        dy -= math.cos(player_angle) * SPEED
    
    if keys[pg.K_d]:
        dx -= math.sin(player_angle) * SPEED
        dy += math.cos(player_angle) * SPEED
    
    # Normalisieren der Bewegung bei Diagonalbewegung
    if dx != 0 and dy != 0:
        length = math.sqrt(dx * dx + dy * dy)
        dx = dx / length * SPEED
        dy = dy / length * SPEED
    
    # Bewegung anwenden mit Kollisionsprüfung
    if dx != 0 or dy != 0:
        next_x = player_x + dx * move_speed
        next_y = player_y + dy * move_speed
        
        # Separate Kollisionsprüfung für X und Y
        # Dies erlaubt das Gleiten an Wänden entlang
        if game_map[int(next_y)][int(player_x)] == 0:
            player_y = next_y
        
        if game_map[int(player_y)][int(next_x)] == 0:
            player_x = next_x
            
        # Überprüfen auf Kollision mit Gegnern und zurückstoßen
        for enemy in enemies:
            if enemy.active:
                enemy_dist = math.sqrt((enemy.x - player_x)**2 + (enemy.y - player_y)**2)
                if enemy_dist < 0.7:  # Kollisionsabstand mit Gegner
                    # Berechne Richtungsvektor vom Gegner weg
                    push_dx = player_x - enemy.x
                    push_dy = player_y - enemy.y
                    
                    # Normalisieren
                    push_length = math.sqrt(push_dx*push_dx + push_dy*push_dy)
                    if push_length > 0:
                        push_dx /= push_length
                        push_dy /= push_length
                        
                        # Spieler leicht wegschieben
                        player_x += push_dx * 0.05
                        player_y += push_dy * 0.05


def add_random_walls():
    """Fügt einige zufällige Wände zur Karte hinzu"""
    # Zunächst Bereich um den Spieler freilassen
    safe_radius = 3  # Größerer Freiraum
    
    # Zufall regulieren mit fester Seed für Reproduzierbarkeit
    np.random.seed(42)
    
    # Weniger Wände für bessere Übersicht
    max_walls = 6
    wall_count = 0
    max_attempts = 30
    attempts = 0
    
    # Füge einzelne Wände hinzu
    while wall_count < max_walls and attempts < max_attempts:
        x, y = np.random.randint(2, MAP_SIZE-2), np.random.randint(2, MAP_SIZE-2)
        # Großer Abstand zum Spieler
        dist_to_player = math.sqrt((x - player_x)**2 + (y - player_y)**2)
        
        if dist_to_player > safe_radius:
            game_map[y][x] = 1
            wall_count += 1
        
        attempts += 1
    
    # Debug-Ausgabe für besseres Verständnis der Karte
    print("Karte generiert:")
    for y in range(MAP_SIZE):
        row = ""
        for x in range(MAP_SIZE):
            if x == int(player_x) and y == int(player_y):
                row += "P "  # Spieler
            elif game_map[y][x] == 1:
                row += "# "  # Wand
            else:
                row += ". "  # Leerer Platz
        print(row)

def spawn_enemies(num_enemies=5):
    """Fügt Gegner an strategischen Positionen hinzu, gut verteilt über die Karte"""
    
    # Potenzielle Positionen vorberechnen
    valid_positions = []
    for y in range(1, MAP_SIZE-1):
        for x in range(1, MAP_SIZE-1):
            if game_map[y][x] == 0:  # Freier Platz
                dist_to_player = math.sqrt((x - player_x)**2 + (y - player_y)**2)
                # Mindestabstand zum Spieler (5-6 Einheiten) für faireres Spiel
                if dist_to_player > 5:
                    valid_positions.append((x + 0.5, y + 0.5))  # Mitte der Zelle
    
    # Gegner spawnen
    spawned = 0
    
    # STRATEGISCHE VERTEILUNG - verschiedene Spawntaktiken
    # 1. Entfernte Positionen für einige Gegner
    # 2. Gut verteilte Positionen für andere (nicht alle an einem Ort)
    # 3. Fallback auf Ecken und gegenüberliegende Positionen
    
    if valid_positions:
        # Sortiere nach Entfernung zum Spieler (absteigend)
        valid_positions.sort(key=lambda pos: -math.sqrt((pos[0] - player_x)**2 + (pos[1] - player_y)**2))
        
        # Erste Gegner an den entferntesten Positionen (max. 50% der Gegner)
        far_enemies = min(num_enemies // 2 + 1, len(valid_positions))
        for i in range(far_enemies):
            x, y = valid_positions[i]
            enemies.append(Enemy(x, y))
            spawned += 1
        
        # Übrige Gegner gut über die Karte verteilen
        if spawned < num_enemies and len(valid_positions) > far_enemies:
            # Nehme Positionen aus dem mittleren Bereich der Liste
            # für gute Verteilung (nicht zu nah, nicht zu fern)
            remaining = min(num_enemies - spawned, len(valid_positions) - far_enemies)
            step = max(1, (len(valid_positions) - far_enemies) // remaining)
            
            for i in range(far_enemies, len(valid_positions), step):
                if spawned >= num_enemies:
                    break
                x, y = valid_positions[i]
                
                # Prüfe, ob der Abstand zu bereits gespawnten Gegnern groß genug ist
                # (für bessere Verteilung)
                too_close = False
                for enemy in enemies:
                    if math.sqrt((x - enemy.x)**2 + (y - enemy.y)**2) < 3.0:
                        too_close = True
                        break
                
                if not too_close:
                    enemies.append(Enemy(x, y))
                    spawned += 1
    
    # Wenn nicht genug Gegner gespawnt wurden, feste Positionen versuchen
    if spawned < num_enemies:
        # Versuche es an entgegengesetzten Ecken und Richtungen
        test_positions = []
        
        # Gegenüberliegende Position vom Spieler
        dx = player_x - MAP_SIZE/2
        dy = player_y - MAP_SIZE/2
        opp_x = max(1.5, min(MAP_SIZE-1.5, player_x - dx * 2))
        opp_y = max(1.5, min(MAP_SIZE-1.5, player_y - dy * 2))
        test_positions.append((opp_x, opp_y))
        
        # Diagonale Ecken
        corners = [(1.5, 1.5), (1.5, MAP_SIZE-1.5), (MAP_SIZE-1.5, 1.5), (MAP_SIZE-1.5, MAP_SIZE-1.5)]
        test_positions.extend(corners)
        
        # Zufällige Positionen in der Nähe von Wänden (guter Deckungsbereich)
        wall_adjacency = []
        for y in range(1, MAP_SIZE-1):
            for x in range(1, MAP_SIZE-1):
                if game_map[y][x] == 0:  # Freier Platz
                    # Prüfe, ob Position neben einer Wand ist
                    has_wall_neighbor = False
                    for ny, nx in [(y-1,x), (y+1,x), (y,x-1), (y,x+1)]:
                        if 0 <= ny < MAP_SIZE and 0 <= nx < MAP_SIZE and game_map[ny][nx] == 1:
                            has_wall_neighbor = True
                            break
                    
                    if has_wall_neighbor:
                        dist_to_player = math.sqrt((x - player_x)**2 + (y - player_y)**2)
                        if dist_to_player > 4:
                            wall_adjacency.append((x + 0.5, y + 0.5))
        
        # Mische die wandnahen Positionen und füge sie zu den Testpositionen hinzu
        random.shuffle(wall_adjacency)
        test_positions.extend(wall_adjacency[:max(0, num_enemies - spawned)])
        
        # Versuche jede Position
        for x, y in test_positions:
            if game_map[int(y)][int(x)] == 0:
                # Prüfe Abstand zu vorhandenen Gegnern
                too_close = False
                for enemy in enemies:
                    if math.sqrt((x - enemy.x)**2 + (y - enemy.y)**2) < 2.0:
                        too_close = True
                        break
                
                if not too_close:
                    enemies.append(Enemy(x, y))
                    spawned += 1
                    if spawned >= num_enemies:
                        break
    
    # Teile dem Benutzer mit, wo Gegner spawnen und in welchem Startzustand
    for enemy in enemies:
        dist = math.sqrt((enemy.x-player_x)**2 + (enemy.y-player_y)**2)
        print(f"Gegner '{enemy.name}' erscheint bei ({enemy.x:.1f}, {enemy.y:.1f}), "
              f"Abstand zum Spieler: {dist:.1f}, Zustand: {enemy.movement_state}")
    
    return spawned

def fire_weapon():
    """Feuert eine Kugel in Blickrichtung des Spielers"""
    global player_ammo, bullets
    if player_ammo <= 0:
        return
    
    # Reduziere Munition
    player_ammo -= 1
    
    # Erstelle neuen Schuss
    new_bullet = Bullet(player_x, player_y, player_angle)
    bullets.append(new_bullet)
    
    # Debug-Ausgabe für Schüsse - immer anzeigen
    print(f"Schuss abgefeuert! Position: ({player_x:.1f}, {player_y:.1f}), Winkel: {player_angle:.2f}")
    print(f"Verbleibende Munition: {player_ammo}")
    
    # Prüfen, ob Gegner in der Nähe sind
    nearby_enemies = []
    for enemy in enemies:
        if enemy.active:
            dist = math.sqrt((enemy.x - player_x)**2 + (enemy.y - player_y)**2)
            if dist < 5.0:  # Gegner in 5 Einheiten Umkreis
                nearby_enemies.append((enemy, dist))
    
    # Zeige die nächsten Gegner an
    if nearby_enemies:
        nearby_enemies.sort(key=lambda x: x[1])  # Sortiere nach Entfernung
        print(f"Gegner in der Nähe:")
        for enemy, dist in nearby_enemies[:3]:  # Maximal 3 Gegner anzeigen
            print(f"  - '{enemy.name}' bei ({enemy.x:.1f}, {enemy.y:.1f}), Entfernung: {dist:.2f}")
    
    # Schusssound abspielen
    if shoot_sound:
        shoot_sound.play()

def update_bullets():
    """Aktualisiert alle aktiven Projektile"""
    # Liste mit allen aktiven Kugeln beibehalten
    global bullets
    # Kopiere die Liste und entferne inaktive Kugeln
    bullets = [bullet for bullet in bullets if bullet.active and bullet.update()]

def update_enemies():
    """Aktualisiert alle Gegner"""
    for enemy in enemies:
        enemy.update()

def draw_help_overlay(screen, font):
    """Zeichnet ein Hilfe-Overlay während des Spiels"""
    # Halbtransparenter Hintergrund
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Schwarz mit 70% Deckkraft
    screen.blit(overlay, (0, 0))
    
    # Überschrift
    title_font = pg.font.SysFont('Arial', 36)
    title_text = title_font.render("HILFE", True, (255, 255, 0))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 40))
    
    # Hilfetext-Box
    help_box = pg.Rect(WIDTH//2 - 300, 100, 600, 400)
    pg.draw.rect(screen, (40, 40, 40), help_box)
    pg.draw.rect(screen, (150, 150, 150), help_box, 2)
    
    # Steuerung
    controls_title = title_font.render("Steuerung", True, (200, 200, 200))
    screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, 120))
    
    # Zweispaltig: Links Steuerung, rechts Spielelemente
    controls = [
        "WASD / Pfeiltasten: Bewegen",
        "Maus: Umschauen/Zielen",
        "Linksklick: Schießen",
        "R: Nachladen (wenn leer)",
        "H / F1: Diese Hilfe anzeigen",
        "ESC: Spiel beenden"
    ]
    
    tips = [
        "Bleibe in Bewegung",
        "Halte Abstand zu Gegnern",
        "Nutze Wände als Deckung",
        "Vermeide Einkreisung",
        "Achte auf deine Munition",
        "Behalte deine Gesundheit im Auge"
    ]
    
    # Steuerungsspalte
    for i, control in enumerate(controls):
        control_text = font.render(control, True, WHITE)
        screen.blit(control_text, (WIDTH//2 - 280, 170 + i * 30))
    
    # Spieltipps-Überschrift
    tips_title = title_font.render("Spieltipps", True, (200, 200, 200))
    screen.blit(tips_title, (WIDTH//2 - tips_title.get_width()//2, 350))
    
    # Tipps-Spalte
    for i, tip in enumerate(tips):
        tip_text = font.render("• " + tip, True, WHITE)
        screen.blit(tip_text, (WIDTH//2 - 280, 390 + i * 30))
    
    # Information zur Gegnerfarbe
    enemy_info_title = font.render("Gegnerverhalten:", True, (255, 200, 100))
    screen.blit(enemy_info_title, (WIDTH//2 + 50, 170))
    
    enemy_states = [
        ("Grün", "Idle/Ruhezustand", (0, 200, 0)),
        ("Blau", "Patrouillierend", (50, 100, 255)),
        ("Rot", "Verfolgend", (255, 50, 50)),
        ("Gelb", "Flüchtend", (255, 255, 0))
    ]
    
    for i, (color_name, state, color) in enumerate(enemy_states):
        # Farbkreis
        pg.draw.circle(screen, color, (WIDTH//2 + 70, 200 + i * 30), 8)
        # Zustandsbeschreibung
        state_text = font.render(f"{color_name}: {state}", True, WHITE)
        screen.blit(state_text, (WIDTH//2 + 90, 192 + i * 30))
    
    # Schließen-Hinweis (pulsierend)
    pulse = (math.sin(pg.time.get_ticks() / 300) * 0.3 + 0.7)  # 0.4 bis 1.0
    close_color = (int(200 * pulse), int(200 * pulse), int(255 * pulse))
    close_text = font.render("Drücke H oder F1 um die Hilfe zu schließen", True, close_color)
    screen.blit(close_text, (WIDTH//2 - close_text.get_width()//2, HEIGHT - 60))


def draw_hud(screen, font):
    """Zeichnet die Spieler-HUD mit Gesundheit, Munition und Punktzahl"""
    # Gesundheitsanzeige
    health_text = font.render(f"Gesundheit: {player_health}", True, WHITE)
    screen.blit(health_text, (10, HEIGHT - 60))
    
    # Gesundheitsbalken
    health_width = int(150 * (player_health / 100))
    pg.draw.rect(screen, RED, (10, HEIGHT - 40, 150, 15))
    pg.draw.rect(screen, GREEN, (10, HEIGHT - 40, health_width, 15))
    
    # Munitionsanzeige
    ammo_text = font.render(f"Munition: {player_ammo}", True, WHITE)
    screen.blit(ammo_text, (200, HEIGHT - 60))
    
    # Punktzahl
    score_text = font.render(f"Punkte: {player_score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, HEIGHT - 60))
    
    # Hilfehinweis (klein, oben rechts)
    help_hint = font.render("Drücke H oder F1 für Hilfe", True, (200, 200, 200))
    screen.blit(help_hint, (WIDTH - help_hint.get_width() - 10, 10))


def test_projection_algorithm():
    """
    Testet den Projektionsalgorithmus mit verschiedenen Szenarien.
    Diese Funktion wird aufgerufen, wenn PROJECTION_TEST_MODE auf True gesetzt ist.
    """
    print("\n==== PROJEKTIONSTESTS ====")
    test_player_x, test_player_y = 5.0, 5.0
    test_fov = math.pi / 3.0  # 60°
    test_screen_width = 800
    
    # Test 1: Objekt direkt vor dem Spieler
    test_angle_degrees = 0  # Spieler schaut nach rechts (0°)
    test_player_angle = math.radians(test_angle_degrees)
    
    # Objekt direkt vor dem Spieler (5, 8) - sollte in der Mitte des Bildschirms sein
    obj_x, obj_y = 8.0, 5.0
    screen_x, rel_angle = compute_screen_x(obj_x, obj_y, test_player_x, test_player_y, 
                                           test_player_angle, test_fov, test_screen_width)
    print(f"Test 1: Objekt bei ({obj_x}, {obj_y}), Spieler bei ({test_player_x}, {test_player_y}), " +
          f"Blickwinkel {test_angle_degrees}°")
    print(f"  -> Bildschirm-X: {screen_x:.1f}, Relativer Winkel: {math.degrees(rel_angle):.1f}°")
    print(f"  -> Erwartung: Mitte des Bildschirms ({test_screen_width/2})")
    
    # Test 2: Objekt links vom Spieler
    obj_x, obj_y = 5.0, 2.0
    screen_x, rel_angle = compute_screen_x(obj_x, obj_y, test_player_x, test_player_y, 
                                           test_player_angle, test_fov, test_screen_width)
    print(f"Test 2: Objekt bei ({obj_x}, {obj_y}), Spieler bei ({test_player_x}, {test_player_y}), " +
          f"Blickwinkel {test_angle_degrees}°")
    print(f"  -> Bildschirm-X: {screen_x:.1f}, Relativer Winkel: {math.degrees(rel_angle):.1f}°")
    print(f"  -> Erwartung: Linke Seite des Bildschirms")
    
    # Test 3: Objekt rechts vom Spieler
    obj_x, obj_y = 5.0, 8.0
    screen_x, rel_angle = compute_screen_x(obj_x, obj_y, test_player_x, test_player_y, 
                                           test_player_angle, test_fov, test_screen_width)
    print(f"Test 3: Objekt bei ({obj_x}, {obj_y}), Spieler bei ({test_player_x}, {test_player_y}), " +
          f"Blickwinkel {test_angle_degrees}°")
    print(f"  -> Bildschirm-X: {screen_x:.1f}, Relativer Winkel: {math.degrees(rel_angle):.1f}°")
    print(f"  -> Erwartung: Rechte Seite des Bildschirms")
    
    # Test 4: Spieler schaut in eine andere Richtung (90°, nach oben)
    test_angle_degrees = 90
    test_player_angle = math.radians(test_angle_degrees)
    
    # Objekt vor dem Spieler (bei 90° = "oben")
    obj_x, obj_y = 5.0, 2.0
    screen_x, rel_angle = compute_screen_x(obj_x, obj_y, test_player_x, test_player_y, 
                                           test_player_angle, test_fov, test_screen_width)
    print(f"Test 4: Objekt bei ({obj_x}, {obj_y}), Spieler bei ({test_player_x}, {test_player_y}), " +
          f"Blickwinkel {test_angle_degrees}°")
    print(f"  -> Bildschirm-X: {screen_x:.1f}, Relativer Winkel: {math.degrees(rel_angle):.1f}°")
    print(f"  -> Erwartung: Mitte des Bildschirms ({test_screen_width/2})")
    
    print("=========================\n")

def main():
    global player_angle, player_x, player_y, player_health, player_ammo, player_score, shoot_sound, shooting_cooldown
    
    # Neue Variable für Hilfe-Overlay
    show_help_overlay = False
    
    # Projektionsalgorithmus testen, wenn Debug-Modus aktiv
    if RENDERING_DEBUG_MODE:
        test_projection_algorithm()
    
    # Pygame initialisieren
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("3D Shooter")
    clock = pg.time.Clock()
    font = pg.font.SysFont('Arial', 18)
    
    # Sound initialisieren
    shoot_sound = None
    try:
        pg.mixer.init()
        # Prüfe ob Sounddatei existiert
        import os
        if os.path.exists('shot.wav'):
            shoot_sound = pg.mixer.Sound('shot.wav')
    except:
        pass  # Sound ist optional
    
    # Alles zurücksetzen
    global enemies, bullets
    enemies = []
    bullets = []
    player_health = 100
    player_ammo = 50
    player_score = 0
    shooting_cooldown = 0
    
    # Karte zurücksetzen (sicherstellen, dass genug freier Platz ist)
    global game_map
    game_map = np.zeros((MAP_SIZE, MAP_SIZE), dtype=int)
    game_map[0, :] = 1  # Obere Wand
    game_map[:, 0] = 1  # Linke Wand
    game_map[MAP_SIZE-1, :] = 1  # Untere Wand
    game_map[:, MAP_SIZE-1] = 1  # Rechte Wand
    
    # Spieler weit weg von den Wänden positionieren
    player_x, player_y = MAP_SIZE // 2, MAP_SIZE // 2
    
    # Nur wenige Wände für bessere Navigation und Übersichtlichkeit
    add_random_walls()
    
    # Verbesserten Startbildschirm anzeigen
    show_start_screen = True
    start_screen_step = 0
    max_steps = 2  # Anzahl der Hilfeseiten
    while show_start_screen:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                    start_screen_step += 1
                    if start_screen_step > max_steps:
                        show_start_screen = False
                elif event.key == pg.K_ESCAPE:
                    pg.quit()
                    return
            elif event.type == pg.MOUSEBUTTONDOWN:
                start_screen_step += 1
                if start_screen_step > max_steps:
                    show_start_screen = False
        
        screen.fill(BLACK)
        
        # Hintergrundbild (einfaches Raster)
        for i in range(0, WIDTH, 40):
            pg.draw.line(screen, (30, 30, 30), (i, 0), (i, HEIGHT), 1)
        for i in range(0, HEIGHT, 40):
            pg.draw.line(screen, (30, 30, 30), (0, i), (WIDTH, i), 1)
        
        title_font = pg.font.SysFont('Arial', 48)
        instr_font = pg.font.SysFont('Arial', 24)
        small_font = pg.font.SysFont('Arial', 18)
        
        # Erste Seite: Titel und grundlegende Steuerung
        if start_screen_step == 0:
            # Halbtransparenter Overlay
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Schwarzer Hintergrund mit 150/255 Alpha
            screen.blit(overlay, (0, 0))
            
            title_text = title_font.render("3D SHOOTER", True, RED)
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//5))
            
            subtitle = instr_font.render("Ein Raycasting-basiertes 3D-Spiel", True, (200, 200, 200))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//5 + 60))
            
            # Steuerungsbox mit Umrandung
            controls_box = pg.Rect(WIDTH//2 - 200, HEIGHT//2 - 80, 400, 200)
            pg.draw.rect(screen, (60, 60, 60), controls_box)
            pg.draw.rect(screen, (120, 120, 120), controls_box, 2)
            
            # Steuerungsüberschrift
            controls_title = instr_font.render("STEUERUNG", True, (255, 200, 0))
            screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//2 - 70))
            
            # Steuerungsliste
            controls = [
                "WASD / Pfeiltasten: Bewegen",
                "Maus: Umschauen/Zielen",
                "Linksklick: Schießen",
                "R: Nachladen (wenn Munition leer)",
                "ESC: Spiel beenden"
            ]
            
            for i, control in enumerate(controls):
                control_text = small_font.render(control, True, WHITE)
                screen.blit(control_text, (WIDTH//2 - control_text.get_width()//2, HEIGHT//2 - 30 + i * 30))
            
            # Navigation
            nav_text = instr_font.render("Drücke LEERTASTE für mehr Infos", True, GREEN)
            screen.blit(nav_text, (WIDTH//2 - nav_text.get_width()//2, HEIGHT - 100))
        
        # Zweite Seite: Spielelemente und Taktik
        elif start_screen_step == 1:
            # Halbtransparenter Overlay
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            page_title = title_font.render("SPIELELEMENTE", True, (255, 200, 0))
            screen.blit(page_title, (WIDTH//2 - page_title.get_width()//2, 40))
            
            # Informationsbox mit Umrandung
            info_box = pg.Rect(WIDTH//2 - 300, 100, 600, 350)
            pg.draw.rect(screen, (40, 40, 40), info_box)
            pg.draw.rect(screen, (100, 100, 100), info_box, 2)
            
            elements = [
                ("GEGNER:", "Rote Kreise mit leuchtenden Augen, verfolgen dich"),
                ("GESUNDHEIT:", "Links unten, wenn leer ist das Spiel vorbei"),
                ("MUNITION:", "Mitte unten, drücke R zum Nachladen"),
                ("PUNKTE:", "Rechts unten, du bekommst 100 Punkte pro Gegner"),
                ("MINIMAP:", "Oben links, zeigt deine Position und Gegner"),
                ("TAKTIK:", "Halte Abstand zu Gegnern und vermeide Einkreisung")
            ]
            
            for i, (title, desc) in enumerate(elements):
                # Titel in gelb
                element_title = instr_font.render(title, True, (255, 255, 0))
                screen.blit(element_title, (WIDTH//2 - 280, 120 + i * 50))
                
                # Beschreibung in weiß
                element_desc = small_font.render(desc, True, WHITE)
                screen.blit(element_desc, (WIDTH//2 - 280 + 150, 120 + i * 50 + 5))
            
            # Navigation
            nav_text = instr_font.render("Drücke LEERTASTE für mehr Infos", True, GREEN)
            screen.blit(nav_text, (WIDTH//2 - nav_text.get_width()//2, HEIGHT - 100))
        
        # Dritte Seite: Letzte Tipps und Start
        elif start_screen_step == 2:
            # Pulsierende Hintergrundeffekte für die letzte Seite
            pulse = (math.sin(pg.time.get_ticks() / 300) * 0.5 + 0.5) * 20 + 10  # 10-30
            
            # Mehrere pulsierende Kreise
            for i in range(3):
                size = pulse * (i + 1) * 3
                alpha = int(200 - i * 60)  # Abnehmende Transparenz
                circle_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
                pg.draw.circle(circle_surf, (255, 0, 0, alpha), (WIDTH//2, HEIGHT//2), size)
                screen.blit(circle_surf, (0, 0))
            
            # Overlay für bessere Lesbarkeit
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            ready_title = title_font.render("BEREIT ZUM KAMPF?", True, (255, 0, 0))
            screen.blit(ready_title, (WIDTH//2 - ready_title.get_width()//2, HEIGHT//4))
            
            # Letzte Tipps in Box
            tips_box = pg.Rect(WIDTH//2 - 250, HEIGHT//2 - 100, 500, 200)
            pg.draw.rect(screen, (30, 30, 30), tips_box)
            pg.draw.rect(screen, (150, 0, 0), tips_box, 3)
            
            tips = [
                "• Bleibe in Bewegung, um Gegnern auszuweichen",
                "• Nutze Wände als Deckung",
                "• Halte deine Munition im Auge",
                "• Gegner in der Nähe verursachen mehr Schaden",
                "• Die Schwierigkeit steigt mit deiner Punktzahl"
            ]
            
            tips_title = instr_font.render("LETZTE TIPPS:", True, (255, 200, 0))
            screen.blit(tips_title, (WIDTH//2 - tips_title.get_width()//2, HEIGHT//2 - 80))
            
            for i, tip in enumerate(tips):
                tip_text = small_font.render(tip, True, WHITE)
                screen.blit(tip_text, (WIDTH//2 - 230, HEIGHT//2 - 40 + i * 30))
            
            # Pulsierende Start-Anweisung
            start_alpha = int((math.sin(pg.time.get_ticks() / 200) * 0.5 + 0.5) * 255)
            start_font = pg.font.SysFont('Arial', 30)
            start_surf = pg.Surface((500, 50), pg.SRCALPHA)
            start_text = start_font.render("Made with <3 by Martin Pfeffer", True, (0, 255, 0, start_alpha))
            start_surf.blit(start_text, (250 - start_text.get_width()//2, 0))
            screen.blit(start_surf, (WIDTH//2 - 250, HEIGHT - 100))
        
        pg.display.flip()
        clock.tick(60)
    
    # Mausfang aktivieren
    pg.mouse.set_visible(False)
    pg.event.set_grab(True)
    
    # Gegner spawnen - verzögertes Spawnen
    pg.time.set_timer(pg.USEREVENT, 8000)  # 8 Sekunden Timer (mehr Zeit zum Erkunden)
    enemy_spawn_scheduled = True
    
    # Mausfang für Mausbewegung
    pg.mouse.set_visible(False)
    pg.event.set_grab(True)
    
    # Spielvariablen
    running = True
    shooting_cooldown = 0
    game_over = False
    
    # Spielschleife
    while running:
        # Delta-Zeit für gleichmäßige Bewegung
        dt = clock.tick(60) / 1000.0
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_r and player_ammo <= 0:
                    # Nachladen wenn leer
                    player_ammo = 50
                elif event.key == pg.K_h or event.key == pg.K_F1:
                    # Toggle Hilfe-Overlay mit H oder F1
                    show_help_overlay = not show_help_overlay
            # Mausbewegung für Drehung
            elif event.type == pg.MOUSEMOTION:
                mouse_rel = pg.mouse.get_rel()
                player_angle += mouse_rel[0] * 0.004
            # Schießen mit Mausklick
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and shooting_cooldown <= 0:
                fire_weapon()
                shooting_cooldown = 10  # Cooldown zwischen Schüssen
            # Verzögertes Spawnen von Gegnern
            elif event.type == pg.USEREVENT and enemy_spawn_scheduled:
                num_spawned = spawn_enemies(2)  # Beginne mit nur 2 Gegnern
                enemy_spawn_scheduled = False
                print(f"Spiel gestartet - {num_spawned} Gegner erschienen!")
        
        # Spieler-Input verarbeiten
        keys = pg.key.get_pressed()
        
        # Game Over Check
        if player_health <= 0:
            game_over = True
        
        if not game_over:
            handle_movement(keys)
            
            # Projektile aktualisieren
            update_bullets()
            
            # Gegner aktualisieren
            update_enemies()
            
            # Schuss-Cooldown
            if shooting_cooldown > 0:
                shooting_cooldown -= 1
                
            # Nachspawnen von Gegnern, wenn alle tot sind
            if not enemy_spawn_scheduled and all(not enemy.active for enemy in enemies):
                spawn_enemies(min(3 + player_score // 300, 8))  # Schwierigkeit steigt mit Punktzahl
        
        # Bildschirm löschen
        screen.fill(BLACK)
        
        # 3D-Umgebung zeichnen
        draw_3d_view(screen)
        
        # Minimap zeichnen
        draw_minimap(screen)
        
        # HUD zeichnen
        draw_hud(screen, font)
        
        # Game Over Anzeige
        if game_over:
            # Halbtransparenter Overlay
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            # Game Over Text
            game_over_font = pg.font.SysFont('Arial', 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, 
                      (WIDTH // 2 - game_over_text.get_width() // 2, 
                       HEIGHT // 2 - game_over_text.get_height() // 2))
            
            score_text = font.render(f"Punktzahl: {player_score}", True, WHITE)
            screen.blit(score_text, 
                      (WIDTH // 2 - score_text.get_width() // 2, 
                       HEIGHT // 2 + 50))
            
            restart_text = font.render("Drücke ESC zum Beenden", True, WHITE)
            screen.blit(restart_text, 
                      (WIDTH // 2 - restart_text.get_width() // 2, 
                       HEIGHT // 2 + 100))
        
        # Hilfe-Overlay anzeigen, wenn aktiviert
        elif show_help_overlay:
            draw_help_overlay(screen, font)
        
        # FPS anzeigen
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        screen.blit(fps_text, (10, 10))
        
        # Bildschirm aktualisieren
        pg.display.flip()
    
    pg.quit()


if __name__ == "__main__":
    main()