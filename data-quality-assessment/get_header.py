from astropy.io import fits

class HDU():
	def __init__(self, file):
		self.data = fits.getdata(file)
		self.header = fits.getheader(file)
		
		# all common keywords

	# instrument specific kewywords
	def kcwi(self):
		self.camera = self.header['CAMERA']

	def nirspec(self):
		pass

	def hires(self):
		pass


