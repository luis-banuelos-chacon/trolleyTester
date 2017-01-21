from modules import GalilController, GalilAxis

galil = GalilController('Galil', '192.168.0.100')
axis = GalilAxis('X', galil)
axis.conversion_factor = 3200
