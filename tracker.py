from datetime import datetime
import math
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


from astropy.coordinates import get_body, GCRS
from astropy.time import Time
import astropy.units as u
from datetime import datetime, timezone

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


xs = [d[1] for d in data] #salva tutte le x della lista data
ys = [d[2] for d in data] #salva tutte le y della lista data
zs = [d[3] for d in data] #salva tutte le z della lista data

plt.figure(figsize=(10,10))
plt.plot(xs, ys, color="orange", linewidth=1, label= "Orion path")
plt.scatter([0], [0], color="deepskyblue", s=300, zorder=5, label="Terra")#zorder= chi può sovbrappore altri elementi il livello il garfico è zorder=1
plt.scatter(xs[0], ys[0], color="green", s=100, zorder=5, label="Inizio")
plt.scatter(xs[-1], ys[-1], color="red", s=100, zorder=5, label="Fine")
plt.axis("equal")



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

#plt.show()

adesso = datetime.now(timezone.utc)
t = Time(adesso)

# GCRS = sistema centrato sulla Terra, come EME2000
luna = get_body('moon', t).gcrs

lx = luna.cartesian.x.to(u.km).value #estrai la x dalla poszione della luna convertendo u in km estarendo il valore
ly = luna.cartesian.y.to(u.km).value #stessa cosa per y
lz = luna.cartesian.z.to(u.km).value #e z

print(f"Luna adesso (geocentrica):")
print(f"  X={lx} km")
print(f"  Y={ly} km")
print(f"  Z={lz} km")

distanza_luna_terra = (lx**2 + ly**2 + lz**2)**0.5
print(f"  Distanza dalla Terra: {distanza_luna_terra:,.0f} km")


t0 = data[0][0] #data d'inizio
t_fine = data[-1][0] #data di fine
times_sec = [(d[0] - t0).total_seconds() for d in data] 

xs = [d[1] for d in data]
ys = [d[2] for d in data]
zs = [d[3] for d in data]
vxs = [d[4] for d in data]
vys = [d[5] for d in data]
vzs = [d[6] for d in data]

# Distanze dalla Terra
def distanza_dalla_terra(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

distanze = [distanza_dalla_terra(d[1], d[2], d[3]) for d in data]

def posizione_a(dt_target):
    t = (dt_target - t0).total_seconds()
    x = np.interp(t, times_sec, xs) #avendo t secondi passati ti trova il valore medio di xs che dovrebbe essere anche se non è un punto esatto in times_sec
    y = np.interp(t, times_sec, ys)
    z = np.interp(t, times_sec, zs)
    return x, y, z

def velocita_a(dt_target):
    t = (dt_target - t0).total_seconds()
    vx = np.interp(t, times_sec, vxs)
    vy = np.interp(t, times_sec, vys)
    vz = np.interp(t, times_sec, vzs)
    return vx, vy, vz

def posizione_luna(dt_target):
    t = Time(dt_target.replace(tzinfo=timezone.utc))
    luna = get_body('moon', t).gcrs
    lx = luna.cartesian.x.to(u.km).value
    ly = luna.cartesian.y.to(u.km).value
    lz = luna.cartesian.z.to(u.km).value
    return lx, ly, lz

def orbita_luna_reale():
    """Calcola la vera orbita della Luna campionando 200 punti nell'ultimo mese"""
    from astropy.time import Time
    import numpy as np
    
    # 200 punti distribuiti in 28 giorni
    tempi = Time(np.linspace(
        Time("2026-03-08").jd,   # un mese prima del lancio
        Time("2026-04-10").jd,   # fine missione
        200
    ), format="jd")
    
    lxs, lys, lzs = [], [], []
    
    for t in tempi:
        luna = get_body('moon', t).gcrs
        lxs.append(luna.cartesian.x.to(u.km).value)
        lys.append(luna.cartesian.y.to(u.km).value)
        lzs.append(luna.cartesian.z.to(u.km).value)
    
    return lxs, lys, lzs
