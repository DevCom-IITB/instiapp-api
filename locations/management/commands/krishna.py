import re
import feedparser
import requests
from notifications.signals import notify
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from external.models import ExternalBlogEntry
from bodies.models import Body
from helpers.misc import table_to_markdown
import sys
from locations.serializers import LocationSerializerMin
from locations.models import Location, LocationLocationDistance


# class ProfileFetcher():
#     """Helper to get dictionary of profiles efficiently."""
#     def __init__(self):
#         self.roll_nos = None

#     def get_roll(self):
#         if not self.roll_nos:
#             self.roll_nos = UserProfile.objects.filter(active=True).values_list('roll_no', flat=True)
#         return self.roll_nos


# profile_fetcher = ProfileFetcher()

'''
Returns adj_list with the distances and updates database for Locations models to contain the node points(if they didn't).
'''
class handle_entry:
    def __init__(self):
        self.coordinates = [[2091, 747], [2189, 756], [2269, 765], [2332, 783], [2483, 729], [2430, 810], [2501, 854], [2554, 899], [2608, 934], [2634, 961], [2741, 916], [2875, 854], [2706, 1014], [2795, 1094], [2848, 1077], [3017, 1014], [2955, 952], [3124, 979], [3204, 952], [3266, 996], [3329, 1014], [3525, 1059], [3614, 1094], [3685, 1112], [3587, 1166], [3783, 1139], [3685, 1210], [3863, 1130], [3943, 1166], [3987, 1192], [4148, 1112], [4237, 1068], [4112, 1041], [3952, 988], [3898, 1246], [3845, 1264], [3783, 1228], [3649, 1370], [3836, 1424], [3934, 1442], [3863, 1531], [3845, 1557], [3881, 1557], [3952, 1575], [4014, 1593], [4050, 1602], [4130, 1620], [4148, 1593], [4192, 1637], [4165, 1700], [4094, 1780], [4148, 1771], [4059, 1798], [4014, 1860], [3916, 1967], [3872, 2011], [3747, 1958], [3836, 2065], [3792, 2118], [3703, 2207], [3622, 2296], [3587, 2350], [3631, 2394], [3631, 2447], [4023, 2590], [4076, 2528], [4112, 2474], [4050, 2456], [4201, 2261], [4281, 2145], [4352, 2145], [4344, 2100], [4201, 2065], [4148, 2047], [4157, 2020], [4219, 1949], [4272, 1860], [4317, 1807], [4468, 1842], [4557, 1735], [4619, 1646], [4593, 1575], [4513, 1611], [4406, 1593], [4361, 1557], [4228, 1522], [4290, 1433], [4361, 1433], [4148, 1504], [4094, 1495], [3979, 1379], [4032, 1308], [4059, 1255], [3970, 1290], [3916, 1290], [3329, 1531], [3266, 1486], [3151, 1397], [3071, 1326], [3124, 1308], [3195, 1264], [3008, 1272], [2875, 1166], [2652, 1228], [2608, 1272], [2599, 1326], [2715, 1522], [2723, 1575], [2706, 1620], [2652, 1646], [2545, 1682], [2528, 1726], [2421, 1691], [2314, 1691], [2109, 1718], [2563, 1744], [2625, 1726], [2670, 1726], [2706, 1735], [2839, 1798], [2857, 1824], [2848, 1860], [2821, 1878], [2430, 2216], [2412, 2269], [2367, 2403], [2243, 2474], [1815, 2715], [1646, 2777], [1531, 2795], [1762, 2893], [1798, 2919], [1878, 3026], [2172, 2937], [2189, 2893], [2376, 2581], [2608, 2376], [2590, 2305], [2554, 2287], [2697, 2154], [2750, 2154], [2893, 2207], [3053, 2056], [3142, 1967], [3275, 1842], [3302, 1842], [3293, 1798], [3124, 1753], [3142, 1691], [3213, 1682], [3293, 1655], [3355, 1673], [3364, 1718], [2421, 2901], [2554, 2652], [2759, 2456], [2928, 2314], [2982, 2261], [3017, 2225], [3382, 2367], [3444, 2376], [3507, 2341], [3160, 2100], [3240, 2011], [3302, 1967], [3364, 1904], [3382, 1869], [3400, 1815], [3427, 1691], [3418, 1629], [3516, 1682], [3329, 2234], [3409, 2136], [3489, 2038], [3551, 1967], [3587, 1931], [3649, 1860], [3703, 1815], [3783, 1718], [3667, 1673], [3845, 1629], [3934, 2723], [3898, 2777], [3845, 2857], [3800, 2919], [4655, 1513], [4780, 1370], [4860, 1272], [4726, 1086], [4593, 943], [4548, 934], [4495, 943], [4335, 1005], [1361, 2732], [1201, 2652], [1121, 2652], [925, 2572], [756, 2501], [721, 2394], [649, 2367], [872, 2198], [1041, 2625], [4780, 1370], [4691, 1335], [4611, 1317], [4566, 1308], [4513, 1290], [4459, 1281], [4397, 1272], [4352, 1255], [4281, 1228], [4210, 1246], [4094, 1237], [4032, 1272], [3970, 1299], [3863, 1272], [4726, 1290], [4762, 1255], [4726, 1219], [4700, 1183], [4673, 1157], [4628, 1219], [4566, 1166], [4539, 1210], [4513, 1210], [4477, 1255], [4851, 1290], [4851, 1246], [4806, 1192], [4771, 1148], [4878, 1130], [4700, 1130], [4717, 1086], [4673, 1050], [4530, 1059], [4450, 1086], [4388, 1148], [4290, 1139], [4228, 1166], [4174, 1192], [4691, 1228], [4477, 1335], [4361, 1317], [4352, 1335], [4326, 1281], [4628, 1077]]


        self.adj_list = {0: {'Hostel 12 Crown of the Campus': 6400.025, 'Hostel 14 Silicon Ship': 2809.529, 'Hostel 13 House of Titans': 33.929, 'Mess for hostels 12 | 13 | 14': 171.209, 1: 9.685}, 'Hostel 12 Crown of the Campus': {0: 6.425}, 'Hostel 14 Silicon Ship': {0: 3.338}, 'Hostel 13 House of Titans': {0: 29.933}, 'Mess for hostels 12 | 13 | 14': {0: 2.378}, 1: {0: 9.685, 2: 6.481}, 2: {1: 6.481, 3: 4.293}, 3: {2: 4.293, 4: 25.717000000000002, 5: 10.333}, 4: {3: 25.717000000000002, 'Hostel 06 Vikings': 1603.969}, 'Hostel 06 Vikings': {4: 5.569}, 5: {3: 10.333, 6: 6.977}, 6: {5: 6.977, 7: 4.8340000000000005, 'ATM - Canara Bank near H6': 145.764}, 'ATM - Canara Bank near H6': {6: 1.9080000000000001}, 7: {6: 4.8340000000000005, 8: 4.141}, 8: {7: 4.141, 9: 1.405, 'Hostel 09 Nawaabon Ki Basti': 5783.225}, 'Hostel 09 Nawaabon Ki Basti': {8: 13.001}, 9: {8: 1.405, 10: 13.474, 12: 7.993}, 10: {9: 13.474, 11: 21.8}, 11: {10: 21.8, 'Hostel 18': 16129.484}, 'Hostel 18': {11: 16.613}, 12: {9: 7.993, 13: 14.321}, 13: {12: 14.321, 14: 3.098, 102: 11.584}, 14: {13: 3.098, 15: 32.53, 'Chaayos Cafe': 729.729}, 'Chaayos Cafe': {14: 1.458}, 15: {14: 32.53, 16: 7.688}, 16: {15: 7.688, 'Hostel 05 Penthouse': 342.225}, 'Hostel 05 Penthouse': {16: 18.549}, 17: {15: 12.674, 18: 7.1290000000000004, 'Tansa House King of campus (Proj. Staff Boys)': 2218.216}, 'Tansa House King of campus (Proj. Staff Boys)': {17: 11.425}, 18: {17: 7.1290000000000004, 19: 5.78}, 19: {18: 5.78, 20: 4.293}, 20: {19: 4.293, 20: 0.0, 'Outdoor Sports Facility': 290.225, 'Hostel 03 Vitruvians': 4635.236}, 'Outdoor Sports Facility': {20: 1.514}, 'Hostel 03 Vitruvians': {20: 15.860000000000001}, 21: {20: 40.441, 22: 9.146, 'Hostel 02 The Wild Ones': 3502.609, 'Indoor Stadium': 486.025}, 'Hostel 02 The Wild Ones': {21: 25.09}, 'Indoor Stadium': {21: 2.509}, 22: {21: 9.146, 'Swimming Pool (new)': 2212.136, 23: 5.365}, 'Swimming Pool (new)': {22: 5.345}, 23: {22: 5.365, 24: 12.52, 25: 10.333}, 24: {23: 12.52, 'Students Activity Centre': 3481.144}, 'Students Activity Centre': {24: 3.625, 26: 7.621}, 25: {23: 10.333, 26: 14.645, 27: 6.481}, 26: {25: 14.645, 'Students Activity Centre': 232.396}, 27: {25: 6.481, 28: 7.696, 'Hostel 01 Queen of the campus': 2811.025}, 'Hostel 01 Queen of the campus': {27: 4.8340000000000005}, 28: {27: 7.696, "Domino's outlet": 1227.809, 29: 2.612}, "Domino's outlet": {28: 4.034, 34: 2.089}, 29: {28: 2.612, 30: 32.321, 34: 10.837}, 30: {29: 32.321, 31: 9.857}, 31: {30: 9.857, 32: 16.354, 192: 13.573}, 32: {31: 16.354, 'Hostel 15 Trident': 29248.056, 33: 28.409}, 'Hostel 15 Trident': {32: 36.297000000000004}, 33: {32: 28.409, 'Hostel 16 Olympus': 19321.4}, 'Hostel 16 Olympus': {33: 19.721}, 34: {35: 3.133, 29: 10.837, "Domino's outlet": 2025.064}, 35: {34: 3.133, 36: 5.14, 37: 49.652}, 36: {35: 5.14, 'State Bank of India Branch': 2.681}, 'State Bank of India Branch': {36: 1.682}, 37: {35: 49.652, 38: 37.885, 95: 128.321}, 38: {37: 37.885, 39: 9.928, 'Central Library': 961.256}, 'Central Library': {38: 1.217, 40: 7.625}, 39: {38: 9.928, 40: 12.962, 89: 28.409, 90: 5.994}, 40: {39: 12.962, 41: 1.0, 'Central Library': 5777.849}, 41: {40: 1.0, 42: 1.296, 180: 5.184, 89: 65.845}, 42: {41: 1.296, 43: 5.365, 'Mathematics Department': 3723.209}, 'Mathematics Department': {42: 5.93}, 43: {42: 5.365, 44: 4.168, 'Old Computer Science Engineering Department': 902.5}, 'Old Computer Science Engineering Department': {43: 3.4}, 44: {43: 4.168, 45: 1.377, 89: 16.004}, 45: {44: 1.377, 46: 6.724, 'Fluid Mechanics and Fluid Power Lab': 289.1}, 'Fluid Mechanics and Fluid Power Lab': {45: 0.389}, 46: {45: 6.724, 47: 1.053, 48: 4.133}, 47: {45: 9.685, 'Tinkerers Lab': 1374.929}, 'Tinkerers Lab': {47: 7.298}, 48: {46: 4.133, 49: 4.698}, 49: {48: 4.698, 50: 11.441, 'Mechanical Engineering Department': 3049.336}, 'Mechanical Engineering Department': {49: 27.361}, 50: {49: 11.441, 51: 2.997, 52: 1.549}, 51: {50: 2.997, 'Industrial Design Centre': 1524.481, 52: 8.65}, 'Industrial Design Centre': {51: 5.002}, 52: {51: 8.65, 53: 5.869, 76: 49.213, 178: 82.57600000000001}, 53: {52: 5.869, 54: 21.053, 'Civil Engineering Department': 3154.225, 'Victor Menezes Convention Centre': 178.216}, 'Civil Engineering Department': {53: 21.361}, 'Victor Menezes Convention Centre': {53: 9.385}, 54: {53: 21.053, 55: 3.872, 'Electrical Engineering Department': 4507.496, 'Electrical Engineering Annexe Building': 900.256}, 'Electrical Engineering Department': {54: 22.985, 176: 18.761}, 'Electrical Engineering Annexe Building': {54: 1.156}, 55: {54: 3.872, 56: 18.434, 57: 4.212}, 56: {54: 28.642, 'Girish Gaitonde Building': 447.241}, 'Girish Gaitonde Building': {175: 6.597}, 57: {55: 4.212, 58: 4.745, 'Seminar Hall': 1601.936, 'Rock Powdering Lab': 907.225}, 'Seminar Hall': {57: 3.536}, 'Rock Powdering Lab': {57: 8.125}, 58: {57: 4.745, 59: 15.842, 'Metallurgical Engineering and Material Science Department': 5501.921, 'Humanities and Social Sciences Department': 2823.161, 'Aerospace Engineering Annexe': 2823.161}, 'Metallurgical Engineering and Material Science Department': {172: 57.748000000000005}, 'Humanities and Social Sciences Department': {58: 16.97}, 'Aerospace Engineering Annexe': {58: 16.97}, 59: {58: 15.842, 60: 14.482000000000001, 'Lecture Hall Complex - 1 & 2': 3042.689, 'Lecture Hall Complex - 3': 174.776}, 'Lecture Hall Complex - 1 & 2': {59: 20.714000000000002, 172: 26.177}, 'Lecture Hall Complex - 3': {59: 5.945}, 60: {59: 14.482000000000001, 61: 4.141, 'Physics Department': 2421.449, 'Chemical Engineering Department': 2943.556}, 'Physics Department': {60: 22.85}, 'Chemical Engineering Department': {60: 30.472, 67: 79.88}, 61: {60: 4.141, 62: 3.872, 161: 6.481}, 62: {61: 3.872, 63: 2.809}, 63: {62: 2.809, 64: 174.113, 160: 40.01}, 64: {63: 174.113, 65: 6.6530000000000005, 181: 25.61}, 65: {64: 6.6530000000000005, 66: 4.212, 'DESE & CESE New Building': 3730.409, 'Cafe Coffee Day': 2927.236}, 'DESE & CESE New Building': {65: 13.13}, 'Cafe Coffee Day': {65: 14.152000000000001}, 66: {65: 4.212, 67: 4.168, 70: 165.841}, 67: {66: 4.168, 68: 60.826, 'Chemical Engineering Department': 11304.644}, 68: {67: 60.826, 69: 19.856, 'Aerospace Engineering Department': 146.304}, 'Aerospace Engineering Department': {68: 2.448}, 69: {68: 19.856, 'ONGC Research Centre': 291.209}, 'ONGC Research Centre': {69: 2.498}, 70: {66: 165.841, 71: 2.089, 'Proposed Building for Tata Centre for Technology': 793.801}, 'Proposed Building for Tata Centre for Technology': {70: 10.585}, 71: {70: 2.089, 72: 21.674}, 72: {71: 21.674, 73: 3.133, 'Energy Science and Engineering': 1370.444}, 'Energy Science and Engineering': {72: 2.813}, 73: {72: 3.133, 74: 0.81}, 74: {73: 0.81, 75: 8.885, 'Centre of Studies in Resources Engineering': 732.721}, 'Centre of Studies in Resources Engineering': {74: 4.45}, 75: {74: 8.885, 76: 10.73, 'Centre for Environmental Science and Engineering': 1310.641}, 'Centre for Environmental Science and Engineering': {75: 15.937000000000001}, 76: {75: 10.73, 51: 23.297, 77: 4.8340000000000005, 'Non- Academic Staff Association': 1298.916}, 'Non- Academic Staff Association': {76: 4.212}, 77: {76: 4.8340000000000005, 78: 24.026, 'Structural integrity Testing and Analysis Centre': 3250.444}, 'Structural integrity Testing and Analysis Centre': {77: 4.6930000000000005, 82: 44.285000000000004}, 78: {77: 24.026, 79: 19.37, 'Electrical Maintenence': 149.776}, 'Electrical Maintenence': {78: 5.92}, 79: {78: 19.37, 80: 11.765, 'OrthoCad Lab': 1031.569, 'Micro Fluidics Lab': 2307.969}, 'OrthoCad Lab': {79: 8.593}, 'Micro Fluidics Lab': {79: 6.273}, 80: {79: 11.765, 81: 5.7170000000000005, 82: 12.461}, 81: {80: 5.7170000000000005, 'Physics Lab (Ist Years)': 1225.064, 'Power House': 231.084}, 'Physics Lab (Ist Years)': {81: 1.289, 82: 10.225}, 'Power House': {81: 6.309}, 82: {80: 12.461, 83: 11.773, 185: 29.768, 'Physics Lab (Ist Years)': 5046.184, 'Structural integrity Testing and Analysis Centre': 19345.964}, 83: {82: 11.773, 84: 3.321, 'SMAmL Suman Mashruwala Advanced Microengineering Lab': 484.625, 'Thermal Hydraulic Test Facility': 3252.249}, 'SMAmL Suman Mashruwala Advanced Microengineering Lab': {83: 1.109}, 'Thermal Hydraulic Test Facility': {83: 6.498}, 84: {83: 3.321, 85: 18.914, 'Cummins Engine Research facility': 529.121, 'Heat Transfer and Thermodynamic Lab': 49.841}, 'Cummins Engine Research facility': {84: 0.65}, 'Heat Transfer and Thermodynamic Lab': {84: 0.89}, 85: {84: 18.914, 88: 6.724, 86: 11.765}, 86: {85: 11.765, 87: 5.041, 'Geotechnical Engg. Lab': 64.1}, 'Geotechnical Engg. Lab': {86: 0.164}, 87: {86: 5.041, 'National Geotechnical Centrifuge Facility': 1444.081}, 'National Geotechnical Centrifuge Facility': {87: 1.5250000000000001}, 88: {87: 50.410000000000004, 85: 6.724, 89: 2.997, 'Heat Pump Lab': 1225.025}, 'Heat Pump Lab': {88: 1.25}, 89: {88: 2.997, 39: 28.409}, 90: {91: 7.8500000000000005, 39: 5.994, 'Inter-disciplinary Programme in Systems and Control Engineering': 1025.024}, 'Inter-disciplinary Programme in Systems and Control Engineering': {90: 2.048}, 91: {90: 7.8500000000000005, 92: 3.5380000000000003, 'NanoTech. & Science Research Centre': 1298.401}, 'NanoTech. & Science Research Centre': {91: 3.697}, 92: {91: 3.5380000000000003, 93: 9.146}, 93: {92: 9.146, 94: 2.916, 211: 59.536}, 94: {93: 2.916}, 95: {96: 5.994, 169: 17.525000000000002, 37: 128.321}, 96: {95: 5.994, 'NCC Office': 4239.641, 97: 21.146}, 'NCC Office': {96: 18.866}, 97: {96: 21.146, 98: 11.441}, 98: {97: 11.441, 99: 3.133, 101: 6.885, 'Hostel 11 Athena (Girls Hostel)': 1771.056}, 'Hostel 11 Athena (Girls Hostel)': {98: 8.82}, 99: {98: 3.133, 100: 6.977, 'Basketball Court': 901.369}, 'Basketball Court': {99: 2.269}, 100: {99: 6.977, 'Hockey Ground': 10827.664, 'Gymkhana Grounds': 9801.1}, 'Hockey Ground': {100: 22.48}, 'Gymkhana Grounds': {100: 9.901}, 101: {100: 35.033, 98: 6.885, 102: 28.925, 'Gymkhana Building': 1227.5, 'Brewberrys Cafe': 2.681}, 'Gymkhana Building': {101: 3.725}, 'Brewberrys Cafe': {101: 1.682}, 102: {101: 28.925, 14: 8.65, 103: 53.573}, 103: {102: 53.573, 104: 3.872}, 104: {103: 3.872, 105: 2.997}, 105: {104: 2.997, 106: 51.872}, 106: {105: 51.872, 107: 2.873}, 107: {106: 2.873, 108: 2.314}, 108: {107: 2.314, 109: 3.592}, 109: {108: 3.592, 110: 12.745000000000001}, 110: {109: 12.745000000000001, 111: 2.225}, 111: {110: 2.225, 112: 12.674, 115: 1.549}, 112: {111: 12.674, 113: 11.449}, 113: {112: 11.449, 114: 42.754}, 114: {113: 42.754, 'Boat House': 1543.201}, 'Boat House': {114: 23.722}, 115: {111: 1.549, 116: 4.168}, 116: {115: 4.168, 117: 2.025}, 117: {116: 2.025, 118: 1.377}, 118: {117: 1.377, 119: 21.658}, 119: {118: 21.658, 120: 1.0}, 120: {119: 1.0, 121: 1.377}, 121: {120: 1.377, 122: 1.053}, 122: {121: 1.053, 123: 267.125, 'National Centre for Mathematics': 8.761}, 'National Centre for Mathematics': {122: 4.765}, 123: {122: 267.125, 124: 3.133, 133: 586.405}, 124: {123: 3.133, 125: 19.981}, 125: {124: 19.981, 126: 20.417}, 126: {125: 20.417, 127: 241.26500000000001, 135: 29.138}, 127: {126: 241.26500000000001, 128: 32.405}, 128: {127: 32.405, 129: 13.549}, 129: {128: 13.549, 130: 62.965, 192: 11066.516}, 130: {129: 62.965, 131: 1.972}, 131: {130: 1.972, 132: 17.849}, 132: {131: 17.849, 133: 94.357}, 133: {132: 94.357, 134: 2.225, 153: 63.297000000000004}, 134: {133: 2.225, 135: 132.31300000000002}, 135: {134: 132.31300000000002, 136: 95.849, 126: 29.138, 154: 36.725}, 136: {135: 95.849, 137: 5.365, 155: 29.201}, 137: {136: 5.365, 138: 1.62}, 138: {137: 1.62, 139: 38.138, 123: 20.417}, 139: {138: 38.138, 140: 2.809}, 140: {139: 2.809, 141: 23.258}, 141: {140: 23.258, 142: 48.401, 157: 10.837}, 142: {141: 48.401, 143: 15.842, 162: 13.385}, 'Hospital': {143: 17.876}, 143: {142: 15.842, 144: 33.314, 'Hospital': 2515.376}, 144: {143: 33.314, 145: 0.729, 166: 12.178}, 145: {144: 0.729, 146: 2.017, 152: 19.22}, 146: {145: 2.017, 147: 30.586000000000002}, 'Kshitij Udyan': {147: 23.490000000000002}, 147: {146: 30.586000000000002, 148: 4.168, 'Kshitij Udyan': 104.40899999999999}, 148: {147: 4.168, 149: 5.122}, 'Tennis Court (new)': {149: 56.45}, 149: {148: 5.122, 150: 7.1290000000000004, 'Tennis Court (new)': 28588.889}, 150: {149: 7.1290000000000004, 151: 4.168}, 151: {152: 2.106, 150: 4.168, 167: 22.189, 168: 5.508}, 'Convocation Hall': {152: 11.93}, 152: {151: 2.106, 168: 4.698, 153: 2288.738, 'Convocation Hall': 60.881, 145: 19.22}, 'Main Gate no. 2': {153: 139.14000000000001}, 153: {152: 2288.738, 154: 79.69, 'Main Gate no. 2': 112922.244}, 154: {153: 79.69, 135: 36.725, 155: 80.441}, 'Hostel 10 Annexe (Girls Hostel)': {155: 16.145}, 155: {136: 29.201, 154: 80.441, 156: 48.725, 'Hostel 10 Annexe (Girls Hostel)': 32.129000000000005}, 'Hostel 10 Phoenix (Girls Hostel)': {156: 6.713}, 156: {155: 48.725, 157: 5.7250000000000005, 'Hostel 10 Phoenix (Girls Hostel)': 789.929}, 'Gulmohar Building': {158: 5.825}, 157: {156: 5.7250000000000005, 158: 2.521, 161: 282.02500000000003, 141: 10.837}, 158: {157: 2.521, 162: 36.074, 159: 153.389, 'Gulmohar Building': 5041.784}, 159: {158: 153.389, 160: 3.9250000000000003, 171: 20.498}, 160: {159: 3.9250000000000003, 161: 5.194, 63: 40.01}, 161: {160: 5.194, 61: 6.481}, 162: {142: 13.385, 158: 36.074, 163: 14.321}, 'Kanwal Rekhi School of Information Technology': {163: 12.746, 172: 12.564}, 163: {162: 14.321, 164: 5.78, 'Kanwal Rekhi School of Information Technology': 9028.721}, 'Computer Centre': {164: 397.8, 173: 197.93}, 164: {163: 5.78, 165: 7.813, 'Computer Centre': 1296.9}, 165: {164: 7.813, 166: 1.549, 174: 38.938}, 'School of Management': {175: 10.82}, 166: {165: 1.549, 167: 3.24, 144: 12.178, 'School of Management': 19.128999999999998}, 167: {166: 3.24, 168: 16.105}, 168: {167: 16.105, 152: 4.698, 151: 5.508, 169: 3.9250000000000003, 170: 8.002}, 169: {168: 3.9250000000000003, 167: 34.92, 95: 17.525000000000002}, 'Main Building': {170: 14.308, 179: 2.61}, 170: {168: 8.002, 'Main Building': 1776.544}, 171: {170: 339.673, 172: 16.004, 159: 20.498}, 172: {171: 16.004, 173: 16.004, 'Kanwal Rekhi School of Information Technology': 911.664, 'Lecture Hall Complex - 1 & 2': 281.921}, 173: {172: 16.004, 174: 8.885, 'Computer Centre': 1877.249, 'Metallurgical Engineering and Material Science Department': 56.164}, 174: {173: 8.885, 175: 2.592, 165: 38.938}, 175: {174: 2.592, 176: 8.885, 'Girish Gaitonde Building': 42.561, 'School of Management': 4102.724}, 'Cafe 92': {176: 2.521}, 176: {175: 8.885, 'Electrical Engineering Department': 1617.161, 'Cafe 92': 1297.225, 177: 4.941}, 'PC Saxena Auditorium / Lecture Theatre': {177: 3.65}, 177: {176: 4.941, 178: 15.809000000000001, 'PC Saxena Auditorium / Lecture Theatre': 628.025}, 178: {179: 15.481, 177: 15.809000000000001, 52: 82.57600000000001, 180: 11.765}, 179: {178: 15.481, 'Main Building': 1090.521}, 180: {41: 5.184, 178: 11.765}, 'Kendriya Vidyalaya ': {181: 2.682}, 181: {64: 25.61, 180: 1204.757, 182: 4.212, 'Kendriya Vidyalaya ': 83.601}, 'Medical Store': {182: 11.365}, 'Uphar': {182: 25.16}, 182: {181: 4.212, 183: 9.209, 'Medical Store': 971.404, 'Uphar': 1467.716}, 'Post Office': {183: 5.45}, 183: {184: 5.869, 182: 9.209, 'Post Office': 126.329}, 184: {183: 5.869, 'Market Gate, Y point Gate no. 3': 2809.841}, 'Market Gate, Y point Gate no. 3': {184: 3.65}, 185: {82: 29.768, 186: 36.074}, 186: {185: 36.074, 187: 16.004, 201: 15555.146}, 187: {186: 16.004, 188: 52.552, 225: 146.978}, 'K-Yantra Lab (CSE Dept.)': {231: 13.725}, 188: {187: 52.552, 189: 38.138, 'K-Yantra Lab (CSE Dept.)': 965.096, 231: 2.612}, 189: {188: 38.138, 190: 2.106}, 190: {189: 2.106, 191: 2.89}, 191: {190: 2.89, 192: 29.444}, 192: {191: 29.444, 31: 13.573}, 193: {129: 32.869, 194: 32.0}, 194: {193: 32.0, 195: 6.4}, 195: {194: 6.4, 196: 44.816}, 196: {195: 44.816, 197: 33.602000000000004}, 197: {196: 33.602000000000004, 198: 12.674}, 198: {197: 12.674, 199: 5.913}, 199: {198: 5.913, 200: 78.29}, 'Padmavati Devi Temple': {200: 5.876}, 200: {199: 78.29, 'Padmavati Devi Temple': 405.476}, 201: {'QIP 1': 1574357.521, 202: 15555.146, 225: 13682.996000000001, 204: 14455.764000000001, 203: 14986.6, 186: 15555.146}, 'QIP 1': {201: 15916.522}, 202: {215: 850.493, 203: 9.146, 'Type1 - 6': 23.4, 201: 15555.146}, 'Type1 - 6': {202: 14.409}, 203: {'Type1 - 7': 264.281, 204: 6.724, 239: 287.738, 202: 9.146, 201: 14986.6}, 'Type1 - 7': {204: 1.2770000000000001}, 204: {'Type1 - 7': 1156.121, 201: 14455.764000000001, 203: 6.724, 202: 31.37, 220: 29.444, 205: 2.106}, 205: {240: 22.025000000000002, 206: 3.133, 204: 2.106}, 206: {224: 6.4, 223: 7.0760000000000005, 207: 2.997, 205: 3.133}, 207: {208: 3.9250000000000003, 241: 3.24}, 208: {243: 5.994, 209: 2.314, 'Type 2B 23': 8465.024}, 'Type 2B 23': {208: 9.488}, 209: {235: 38.165, 210: 5.7700000000000005, 'CSRE C': 4495.724}, 'CSRE C': {209: 11.213000000000001}, 210: {209: 5.7700000000000005, 211: 5.365}, 211: {210: 5.365, 212: 13.537, 238: 6.724, 93: 59.536, 'Bungalow A16 ': 1311.625}, 'Bungalow A16 ': {211: 16.921}, 212: {213: 5.069, 'Bungalow A15 ': 41.929, 211: 13.537}, 'Bungalow A15 ': {212: 5.965}, 213: {214: 4.573, 'Bungalow A14 ': 7.724, 212: 5.069}, 'Bungalow A14 ': {213: 6.7250000000000005}, 214: {213: 4.573}, 215: {202: 850.493, 216: 745.093, 'Type 2B 22': 2655.404}, 'Type 2B 22': {215: 808.253}, 216: {215: 745.093, 217: 2.521, 226: 15.625, 'Type1 - 18': 446.625, 'Type1 - 16': 1444.169}, 'Type1 - 18': {216: 6.066}, 'Type1 - 16': {216: 1.613}, 217: {239: 349.713, 218: 2.592, 227: 8.002, 'Proposed Type H1 Building': 3876.761}, 'Proposed Type H1 Building': {217: 36.605000000000004}, 218: {217: 2.592, 219: 1.972, 'Type1 - 14': 444.136, 'Type H1 - 12': 2116.441}, 'Type1 - 14': {218: 3.577}, 'Type H1 - 12': {218: 2.557}, 219: {218: 1.972, 220: 1.405, 228: 11.317}, 220: {239: 250.226, 219: 1.405, 'Type1 - 13': 6401.296, 222: 11.53}, 'Type1 - 13': {220: 7.696}, 221: {222: 6.6530000000000005, 'Type H1 - 5': 2121.776}, 'Type H1 - 5': {221: 7.892}, 222: {221: 6.6530000000000005, 223: 2.665, 220: 11.53}, 223: {224: 0.676, 222: 2.665, 'Type H1 - 6': 446.041}, 'Type H1 - 6': {223: 5.482}, 224: {223: 0.676, 206: 6.4, 'Type H1 - 8': 846.041}, 'Type H1 - 8': {224: 5.882000000000001}, 225: {201: 13682.996000000001, 226: 141.101, 'QIP 2': 5482.664, 187: 146.978}, 'QIP 2': {225: 158.993}, 226: {227: 1.936, 216: 15.625}, 227: {226: 1.936, 217: 8.002, 228: 4.941}, 228: {227: 4.941, 230: 9.028, 229: 3.161}, 229: {228: 3.161, 'Vidya Niwas': 1388.6}, 'Vidya Niwas': {229: 20.969}, 230: {228: 9.028, 231: 31.684, 'C22, B wing, Vindya': 453.824}, 'C22, B wing, Vindya': {230: 54.224000000000004}, 231: {230: 31.684, 'C22, A wing, Sahyadri': 2809.729, 'K-Yantra Lab (CSE Dept.)': 5633.1, 232: 2.225, 188: 2.612}, 'C22, A wing, Sahyadri': {231: 3.5380000000000003}, 232: {244: 190.906, 231: 2.225}, 233: {244: 173.77, 234: 20.53}, 234: {'B 23 Aravali': 15142.225, 233: 20.53, 235: 7.1290000000000004}, 'B 23 Aravali': {234: 28.354}, 235: {234: 7.1290000000000004, 209: 38.165}, 236: {237: 9.685, 'Bungalow A19 ': 1455.664, 'CSRE D': 536.396}, 'Bungalow A19 ': {236: 13.108}, 'CSRE D': {236: 7.925}, 237: {236: 9.685, 238: 4.573, 'Bungalow A18 ': 13.9, 'CSRE A': 576.049, 'CSRE B': 1601.521}, 'Bungalow A18 ': {237: 4.909}, 'CSRE A': {237: 0.625}, 'CSRE B': {237: 3.121}, 238: {237: 4.573, 211: 6.724, 'Bungalow A17 ': 86.329}, 'Bungalow A17 ': {238: 5.41}, 239: {220: 250.226, 217: 349.713}, 240: {'Type H2 - 18': 8521.6, 205: 22.025000000000002}, 'Type H2 - 18': {240: 66.06400000000001}, 241: {242: 13.780000000000001, 'Type H2 - 19': 46.0, 207: 3.24}, 'Type H2 - 19': {241: 10.036}, 242: {241: 13.780000000000001, 'Type H2 - 20': 11.916}, 'Type H2 - 20': {242: 2.9250000000000003}, 243: {'Type H2 - 21': 5627.304, 208: 5.994}, 'Type H2 - 21': {243: 7.929}, 244: {233: 173.77, 232: 190.906, 'Tulsi C': 62578.961}, 'Tulsi C': {244: 141.461}}
    

    '''Caution: Avoid executing the update function during active requests as it may cause significant delays (~20s). If any modifications need to be made to the adj_list, it is essential to ensure that the adj_list is updated accordingly, including the distances between nodes. '''

    def update(self):
        for x in self.adj_list:
            if type(x) != str:
                for y in self.adj_list[x]:
                    if type(y) != str:
                        self.adj_list[x][y] = abs(0.001 * ((self.coordinates[x][0]  - (self.coordinates[y][0]) )**2 +
                                        (self.coordinates[x][1] - (self.coordinates[y][1] ))**2))
                    else:
                        try:
                            x_cor = Location.objects.filter(name=y)[0].pixel_x
                            y_cor = Location.objects.filter(name=y)[0].pixel_y
                            if x_cor is None or y_cor is None:
                                x_cor=0
                                y_cor=0
                        except IndexError:
                            x_cor =0
                            y_cor=0

                        self.adj_list[x][y] = abs(0.001 * ((self.coordinates[x][0]  - x_cor) )**2 +
                                            (self.coordinates[x][1] - y_cor)**2)
                        
            else:
                try:
                    loc = Location.objects.filter(name=x)[0]
                    x_cor = loc.pixel_x
                    y_cor = loc.pixel_y
                    if x_cor is None or y_cor is None:
                        x_cor=0
                        y_cor=0

                except IndexError:
                    x_cor =0
                    y_cor =0
            
                for y in self.adj_list[x]:
                    if type(y) != str:
                        self.adj_list[x][y] = abs(0.001 * ((x_cor  - (self.coordinates[y][0]) )**2 +
                                        (y_cor - (self.coordinates[y][1] ))**2))
                    else:
                        try:
                            x_pix = Location.objects.filter(name=y)[0].pixel_x
                            y_pix = Location.objects.filter(name=y)[0].pixel_y
                            
                        except IndexError:
                            x_pix =0
                            y_pix=0
                        if x_pix is None or y_pix is None:
                            x_pix=0
                            y_pix=0
                        
                        self.adj_list[x][y] = abs(0.001 * ((x_cor  - x_pix) )**2 +
                                            (y_cor - y_pix)**2)
            # Need to run this once to update the database with given new or updated node points.
            i = 0
            loc_list = []
            for p in self.coordinates:
                loc, c = Location.objects.get_or_create(pixel_x=p[0], pixel_y=p[1], name="Node" + str(i))
                loc_list.append(loc)
                i += 1
    
    '''Gets the nearest Node near a location on the map.'''
    def get_nearest(self, loc):
        if "Node" in loc:
            l = int(loc.replace("Node", ""))
            return l
        min_dist = sys.maxsize
        nearest_loc = ""
        try:
            sts = self.adj_list
            sets = sts[loc] 
            for i in sets:
                if type(sets[i]) != str:
                    if sets[i]<=min_dist :
                        min_dist = sets[i]
                        nearest_loc = i
        except KeyError:
            raise Exception("Invalid Location")
        return nearest_loc
    
    '''Returns the adj_list which contains only the node points and nothing else.'''
    def graph(self):
        new_adjoint_list ={}
        for i in self.adj_list:
            if type(i) != str:
                new_adjoint_list[i] = {}
                for j in self.adj_list[i]:
                    if type(j)!=str:
                        new_adjoint_list[i][j] =self.adj_list[i][j]
        return new_adjoint_list
                
                
def dijkstra(graph, start, goal):
    shortest_dist = {}
    track_pred = {}
    unseenNodes=graph
    inf = sys.maxsize
    track_path = []
    for node in unseenNodes:
        shortest_dist[node] = inf
    shortest_dist[start] = 0
    while unseenNodes:
        min_distNode = None
        for node in unseenNodes:
            if min_distNode is None:
                min_distNode = node
            elif shortest_dist[node] < shortest_dist[min_distNode]:
                min_distNode = node
        path_options = graph[min_distNode].items()
        for child_node, weight in path_options:
            if weight + shortest_dist[min_distNode] < shortest_dist[child_node]:
                shortest_dist[child_node] = weight + shortest_dist[min_distNode]
                track_pred[child_node] = min_distNode
        unseenNodes.pop(min_distNode)
    currentNode = goal
    while currentNode != start:
        try:
            track_path.insert(0, currentNode)
            currentNode = track_pred[currentNode]
        except KeyError:
            print(f"Path is not reachable start : {start}, end:{goal}")
            break
    track_path.insert(0, start)
    if shortest_dist[goal] != inf:
        print(str(shortest_dist[goal]))
        print(str(track_path))

        return track_path


    # for i in range(0, len(coordinates)):
    #     loc1 = loc_list[i]
    #     print(adj_list[i])
    #     for loc2_ind in adj_list[i]:
    #         loc2 = loc_list[loc2_ind]
    #         dist = adj_list[i][loc2_ind]
    #         lld = LocationLocationDistance.objects.filter(location1__id=loc1.id, location2__id=loc2.id).first()
    #         if not lld:
    #             LocationLocationDistance.objects.create(
    #                 location1=loc1, location2=loc2, distance=dist)
    #         else:
    #             lld.distance = dist
    #             lld.save()

class Command(BaseCommand):
    help = 'Updates the external blog database'

    def handle(self, *args, **options):
        """Run the chore."""

        handle_entry(settings.EXTERNAL_BLOG_URL)
        self.stdout.write(self.style.SUCCESS('External Blog Chore completed successfully'))


''' This command gets the nearest points for some x, y coordinates. Although a simliar function is defined in views.py'''
def fn_nearest_points(request):
    xcor = request.data2["xcor"]
    ycor = request.data2["ycor"]

    locations = {}
    if xcor is not None and ycor is not None:
        try:
            xcor = int(xcor)
            ycor = int(ycor)
        except TypeError:
            data = {"detail": "Invalid Coordinates "}
            return data
        if 'only_nodes' in request.data2:
            filtered_locations = Location.objects.filter(Q(name__contains="Node"), pixel_x__range=[xcor - 1200, xcor + 1200], pixel_y__range=[ycor - 1200, ycor + 1200])
            #filtered_locations = location.filter(pixel_x__range=[xcor - 400, xcor + 400], pixel_y__range=[ycor - 400, ycor + 400])
        else:
            location = Location
            filtered_locations = location.objects.filter(
            pixel_x__range=[xcor - 400, xcor + 400], pixel_y__range=[ycor - 400, ycor + 400])
        if len(filtered_locations) >= 2:
            nearest_point_dist = sys.maxsize
            second_nearest_point_dist = sys.maxsize
            npi = 0
            snpi = 1
            for a in range(0, len(filtered_locations) - 1):
                i = filtered_locations[a]
                distance = 0.001 * ((i.pixel_x - xcor) ^ 2 + (i.pixel_y - ycor) ^ 2)
                if distance <= nearest_point_dist:
                    second_nearest_point_dist = nearest_point_dist
                    snpi = npi
                    npi = a
                    nearest_point_dist = distance
                elif distance <= second_nearest_point_dist:
                    second_nearest_point_dist = distance
                    snpi = a

        elif len(filtered_locations) < 2:
            filtered_locations = Location.objects.filter(
                pixel_x__range=[xcor - 1200, xcor + 1200], pixel_y__range=[ycor - 1200, ycor + 1200])
            nearest_point_dist = sys.maxsize
            second_nearest_point_dist = sys.maxsize
            npi = 0
            snpi = 1
            for a in range(0, len(filtered_locations) - 1):
                i = filtered_locations[a]
                distance = 0.001 * ((i.pixel_x - xcor) ^ 2 + (i.pixel_y - ycor) ^ 2)
                if distance <= nearest_point_dist:
                    second_nearest_point_dist = nearest_point_dist
                    snpi = npi
                    npi = a
                    nearest_point_dist = distance
                elif distance <= second_nearest_point_dist:
                    second_nearest_point_dist = distance
                    snpi = a
        if len(filtered_locations) >= 2:
            locations[0] = LocationSerializerMin(filtered_locations[npi]).data
            locations[1] = LocationSerializerMin(filtered_locations[snpi]).data

            return locations
        else:
            return {"detail": "No Locations"}
