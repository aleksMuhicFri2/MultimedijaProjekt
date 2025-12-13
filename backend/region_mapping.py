OB_TO_REGION = {}

from name_utils import normalize_name

def add(region_key, municipalities):
    for m in municipalities:
        OB_TO_REGION[normalize_name(m)] = region_key


add("gorenjska", [
    "Bled", "Bohinj", "Cerklje na Gorenjskem", "Gorenja vas-Poljane",
    "Gorje", "Jesenice", "Jezersko", "Kranj", "Kranjska Gora",
    "Naklo", "Preddvor", "Radovljica", "Šenčur", "Škofja Loka",
    "Tržič", "Železniki", "Žiri", "Žirovnica"
])

add("goriska", [
    "Ajdovščina", "Bovec", "Brda", "Cerkno", "Idrija", "Kanal",
    "Kobarid", "Miren-Kostanjevica", "Nova Gorica", "Renče-Vogrsko",
    "Šempeter-Vrtojba", "Tolmin", "Vipava"
])

add("obalno-kraska", [
    "Ankaran", "Izola", "Komen", "Koper", "Piran", "Sežana",
    "Divača", "Hrpelje-Kozina"
])

add("notranjsko-kraska", [
    "Bloke", "Cerknica", "Ilirska Bistrica",
    "Loška dolina", "Pivka", "Postojna", "Loški Potok"
])

add("osrednjeslovenska", [
    "Borovnica", "Brezovica", "Dobrepolje", "Dobrova-Polhov Gradec",
    "Dol pri Ljubljani", "Domžale", "Grosuplje", "Horjul", "Ig",
    "Ivančna Gorica", "Kamnik", "Komenda", "Litija", "Ljubljana",
    "Log-Dragomer", "Logatec", "Lukovica", "Medvode", "Mengeš",
    "Moravče", "Škofljica", "Trzin", "Velike Lašče", "Vodice",
    "Vrhnika", "Šmartno pri Litiji"
])

add("zasavska", [
    "Hrastnik", "Trbovlje", "Zagorje ob Savi"
])

add("savinjska", [
    "Braslovče", "Celje", "Dobje", "Dobrna", "Gornji Grad", 
    "Kozje", "Laško", "Ljubno", "Luče", "Mozirje", "Nazarje", 
    "Polzela", "Prebold", "Rečica ob Savinji", "Rogaška Slatina",
    "Rogatec", "Šmartno ob Paki", "Šoštanj", "Štore", "Tabor",
    "Velenje", "Vitanje", "Vojnik", "Zreče","Bistrica ob Sotli",
    "Podčetrtek", "Solčava", "Šentjur", "Šmarje pri Jelšah",
    "Vransko", "Žalec"
])

add("koroska", [
    "Črna na Koroškem", "Dravograd", "Mežica", "Mislinja",
    "Muta", "Podvelka", "Prevalje", "Radlje ob Dravi",
    "Ravne na Koroškem", "Ribnica na Pohorju", "Slovenj Gradec",
    "Vuzenica",
])

add("podravska", [
    "Benedikt", "Cerkvenjak", "Destrnik", "Dornava", "Duplek",
    "Gorišnica", "Hajdina", "Hoče-Slivnica", "Jurovski Dol",
    "Kidričevo", "Kungota", "Lenart", "Lovrenc na Pohorju",
    "Majšperk", "Makole", "Maribor", "Miklavž na Dravskem Polju",
    "Oplotnica", "Ormož", "Pesnica", "Podlehnik", "Poljčane",
    "Ptuj", "Rače-Fram", "Ruše", "Selnica ob Dravi",
    "Slovenska Bistrica", "Slovenske Konjice", "Starše",
    "Sveta Ana", "Sveta Trojica v Slov. goricah", "Sveti Andraž v Slov. goricah",
    "Sveti Jurij v Slov. Goricah", "Šentilj", "Žetale", "Cirkulane",
    "Juršinci", "Križevci", "Markovci", "Središče ob Dravi",
    "Sveti Tomaž", "Trnovska vas", "Videm", "Zavrč",
])

add("pomurska", [
    "Apače", "Beltinci", "Črenšovci", "Dobrovnik", "Gornja Radgona",
    "Gornji Petrovci", "Grad", "Hodoš", "Kobilje", "Kuzma", "Lendava",
    "Moravske Toplice", "Murska Sobota", "Odranci", "Puconci",
    "Radenci", "Razkrižje", "Rogašovci", "Šalovci", "Tišina",
    "Turnišče", "Velika Polana", "Veržej", "Cankova", "Ljutomer",
    "Sveti Jurij ob Ščavnici"
])

add("posavska", [
    "Brežice", "Kostanjevica na Krki", "Krško", "Radeče", "Sevnica"
])

add("jugovzhodna", [
    "Črnomelj", "Dolenjske Toplice", "Kočevje", "Loški Potok",
    "Metlika", "Mirna", "Mirna Peč", "Novo mesto", "Osilnica",
    "Ribnica", "Semič", "Sodražica", "Straža", "Šentjernej",
    "Šmarješke Toplice", "Trebnje", "Žužemberk", "Kostel",
    "Mokronog - Trebelno", "Šentrupert", "Škocjan"
])



