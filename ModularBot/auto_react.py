from random import choice
from re import compile

from discord import Embed

from .util import ModularUtil
from config import ModularBotConst, Expression


class Reaction:
	__BAD_EXPRESSION = [
		"Katanya kalo pura pura gila\ngila beneran",
		"In the name of goddess Aqua\nI doakan U cepet mampus",
		"Yg Patah Tumbuh\nYg Hilang Otak Kau",
		"Kamu Kok Betah Banget Jadi Goblok",
		"Akhlak Lu Benerin Dulu\nBiar Arwah Lu Lancar Ditarik Dishub",
		"Siang Siang Makan Semangka\nMalam Malam Makan Belimbing\nSumpah Aku Gak Menyangka\nMukamu Kamu Mirip Anjing",
		"Tanam Tanam Ubi\nTak Perlu Dibaje\nBacot Kau Babi\nKita Gelud Saje",
		"Ringan Sama Dijinjing\nBerat Sama Dipikul\nNgeselin Lu Anjing\nSini Gw Pukul",
		"Mukanya menghina tuhan banget",
		"Mulutnya kaya orang ga punya agama",
	]
	__GOOD_EXPRESSION = [
		'Sebuah hadist meriwayatkan \n`Dan (ingatlah juga) tatkala Tuhan kalian memaklumatkan, " \
            ""Sesungguh­nya jika kalian bersyukur (atas nikmat-Ku), pasti Kami akan menambah (nikmat) kepada kalian; " \
            "dan jika kalian mengingkari (nikmat-Ku), maka sesungguhnya azab-Ku sangatlah pedih. \n\nQ.S Ibrahim-07`',
		'Sebuah hadist meriwayatkan \n`“Dari Ibnu Abbas, dia berkata : Nabi SAW bersabda : “Dua kenikmatan, " \
            "kebanyakan manusia tertipu pada keduanya, yaitu kesehatan dan waktu." \n\n-H.R Bukhari`',
		'Sebuah hadist meriwayatkan \n`“Allah berfirman dalam hadits qudsi-Nya: “wahai anak Adam, bahwa selama engkau mengingat Aku, " \
            "berarti engkau mensyukuri Aku, dan apabila engkau melupakan Aku, berarti engkau telah mendurhakai Aku!” \n\n-H.R Thabrani`',
		'Sebuah hadist meriwayatkan \n`“Barang siapa yang tidak bersyukur kepada manusia, berarti ia tidak bersyukur kepada Allah." ""\n\nH.R Ahmad dan Baihaqi`',
		'Sebuah hadist meriwayatkan \n` “Jadilah orang yang wara’, maka engkau akan menjadi hamba yang paling berbakti. " \
            "Jadilah orang yang qana’ah, maka engkau akan menjadi hamba yang paling bersyukur.” \n\n-HR. Ibnu Majah no. 3417, dishahihkan Al Albani dalam Shahih Ibni Majah`',
		'Sebuah hadist meriwayatkan \n`“Seorang mukmin itu sungguh menakjubkan, karena setiap perkaranya itu baik. " \
            "Namun tidak akan terjadi demikian kecuali pada seorang mu’min sejati. Jika ia mendapat kesenangan, ia bersyukur, dan itu baik baginya. " \
            "Jika ia tertimpa kesusahan, ia bersabar, dan itu baik baginya.” \n\n-HR. Muslim no.7692`',
		'Sebuah hadist meriwayatkan \n`“Ketika itu hujan turun di masa Nabi Shallallahu’alaihi Wasallam, lalu Nabi bersabda, " \
            "‘Atas hujan ini, ada manusia yang bersyukur dan ada yang kufur nikmat. Orang yang bersyukur berkata, ‘Inilah rahmat Allah.’ " \
            "Orang yang kufur nikmat berkata, ‘Oh pantas saja tadi ada tanda begini dan begitu. \n\n-HR. Muslim no.73`',
	]

	__REACT_TO = {
		"bad_words": compile(Expression.BAD_WORDS_REGEX),
		"stress": compile(Expression.STRESS_WORDS_REGEX),
		"holy_word": compile(Expression.HOLY_WORDS_REGEX),
	}

	__RESPONSE = {
		"bad_words": [
			"Astaugfirullah...",
			"Ngak boleh gitu",
			"Goblok",
			"Yang sopan dong",
			"Utekke ng silet",
			"Bocah goblok",
			"Lambemu su",
		],
		"stress": [
			"blok",
			"Halo Pak Nasikind, ada yang perlu di ruqyah",
			"Stress",
			"Goblok",
			"Kalo stress jangan disini",
			"Ingatlah nak 2D itu ngak nyata",
			"3D > 2D",
		],
		"holy_word": [
			"Masyallah",
			"Subhanallah",
			"Stay halal brader",
			"Alhamdulillah",
			"Allah akbar",
		],
	}

	@classmethod
	def message_generator(cls, message: str) -> str | Embed:
		clean: str = message.lower()
		for type, item in cls.__REACT_TO.items():
			if item.search(clean):
				sendtype: bool = choice((True, False))
				exprss: str = choice(cls.__RESPONSE[type])
				if not sendtype:
					rand_express: str = (
						choice(cls.__BAD_EXPRESSION)
						if type == "bad_words" or type == "stress"
						else choice(cls.__GOOD_EXPRESSION)
					)
					e: Embed = Embed(
						title=exprss,
						description=rand_express,
						color=ModularUtil.convert_color(
							choice(ModularBotConst.Color.RANDOM)
						),
					)
					return e
				return exprss
