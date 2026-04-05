from datetime import datetime
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
data=[]

with open ("Artemis2.asc", "r") as file:
    for line in file:
        line=line.strip()
        
        if not line or "=" in line or line.startswith("COMMENT") or line.startswith("META"):
            continue
        
        parts=line.split() # divide la colonna dei dati in parti dove ci sono spazi
        # print(parti[5])
        
        if len(parts)==7:
            timestamp=datetime.fromisoformat(parts[0])
            
            x=float(parts[1])
            y=float(parts[2])
            z=float(parts[3])
            Vx=float(parts[4])
            Vy=float(parts[5])
            Vz=float(parts[6])
            
            data.append ((timestamp, x, y ,z , Vx, Vy, Vz))
            
print(f"Coordinate lette: {len(data)}")
print()

def distanza_dalla_terra(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

# Calcoliamo la distanza per ogni punto
distanze = [distanza_dalla_terra(d[1], d[2], d[3]) for d in data]

print("=== DISTANZE DALLA TERRA ===")
print(f"  All'inizio:  {distanze[0]:,.0f} km")
print(f"  Massima:     {max(distanze):,.0f} km  (punto più lontano dalla Terra)")
print(f"  Alla fine:   {distanze[-1]:,.0f} km")

xs = [d[1] for d in data] #salva tutte le x della lista data
ys = [d[2] for d in data] #salva tutte le y della lista data
zs = [d[3] for d in data] #salva tutte le z della lista data

plt.figure(figsize=(10,10))
plt.plot(xs, ys, color="orange", linewidth=1, label= "Orion path")
plt.scatter([0], [0], color="deepskyblue", s=300, zorder=5, label="Terra")#zorder= chi può sovbrappore altri elementi il livello il garfico è zorder=1
plt.scatter(xs[0], ys[0], color="green", s=100, zorder=5, label="Inizio")
plt.scatter(xs[-1], ys[-1], color="red", s=100, zorder=5, label="Fine")
plt.axis("equal")
plt.show()


fig=plt.figure(figsize=(12,10))
ax= fig.add_subplot(111, projection='3d')
ax.plot(xs, ys, zs, color="orange", linewidth=1, label="Orion")
ax.scatter([0], [0], [0], color="deepskyblue", s=300, label="Terra")
ax.scatter(xs[0],  ys[0],  zs[0],  color="green", s=100, label="Inizio")
ax.scatter(xs[-1], ys[-1], zs[-1], color="red",   s=100, label="Fine")

ax.set_xlabel("X (km)")
ax.set_ylabel("Y (km)")
ax.set_zlabel("Z (km)")
ax.set_title("Artemis II — Traiettoria 3D")
ax.legend()

plt.show()