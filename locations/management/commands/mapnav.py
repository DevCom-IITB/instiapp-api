from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
import sys
from locations.serializers import LocationSerializerMin
from locations.models import Location
import json

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
Returns adj_list with the distances and updates database for
Locations models to contain the node points(if they didn't).
'''
class handle_entry:
    def __init__(self):
        self.coordinates = [[2091, 747],
                            [2189, 756],
                            [2269, 765],
                            [2332, 783],
                            [2483, 729],
                            [2430, 810],
                            [2501, 854],
                            [2554, 899],
                            [2608, 934],
                            [2634, 961],
                            [2741, 916],
                            [2875, 854],
                            [2706, 1014],
                            [2795, 1094],
                            [2848, 1077],
                            [3017, 1014],
                            [2955, 952],
                            [3124, 979],
                            [3204, 952],
                            [3266, 996],
                            [3329, 1014],
                            [3525, 1059],
                            [3614, 1094],
                            [3685, 1112],
                            [3587, 1166],
                            [3783, 1139],
                            [3685, 1210],
                            [3863, 1130],
                            [3943, 1166],
                            [3987, 1192],
                            [4148, 1112],
                            [4237, 1068],
                            [4112, 1041],
                            [3952, 988],
                            [3898, 1246],
                            [3845, 1264],
                            [3783, 1228],
                            [3649, 1370],
                            [3836, 1424],
                            [3934, 1442],
                            [3863, 1531],
                            [3845, 1557],
                            [3881, 1557],
                            [3952, 1575],
                            [4014, 1593],
                            [4050, 1602],
                            [4130, 1620],
                            [4148, 1593],
                            [4192, 1637],
                            [4165, 1700],
                            [4094, 1780],
                            [4148, 1771],
                            [4059, 1798],
                            [4014, 1860],
                            [3916, 1967],
                            [3872, 2011],
                            [3747, 1958],
                            [3836, 2065],
                            [3792, 2118],
                            [3703, 2207],
                            [3622, 2296],
                            [3587, 2350],
                            [3631, 2394],
                            [3631, 2447],
                            [4023, 2590],
                            [4076, 2528],
                            [4112, 2474],
                            [4050, 2456],
                            [4201, 2261],
                            [4281, 2145],
                            [4352, 2145],
                            [4344, 2100],
                            [4201, 2065],
                            [4148, 2047],
                            [4157, 2020],
                            [4219, 1949],
                            [4272, 1860],
                            [4317, 1807],
                            [4468, 1842],
                            [4557, 1735],
                            [4619, 1646],
                            [4593, 1575],
                            [4513, 1611],
                            [4406, 1593],
                            [4361, 1557],
                            [4228, 1522],
                            [4290, 1433],
                            [4361, 1433],
                            [4148, 1504],
                            [4094, 1495],
                            [3979, 1379],
                            [4032, 1308],
                            [4059, 1255],
                            [3970, 1290],
                            [3916, 1290],
                            [3329, 1531],
                            [3266, 1486],
                            [3151, 1397],
                            [3071, 1326],
                            [3124, 1308],
                            [3195, 1264],
                            [3008, 1272],
                            [2875, 1166],
                            [2652, 1228],
                            [2608, 1272],
                            [2599, 1326],
                            [2715, 1522],
                            [2723, 1575],
                            [2706, 1620],
                            [2652, 1646],
                            [2545, 1682],
                            [2528, 1726],
                            [2421, 1691],
                            [2314, 1691],
                            [2109, 1718],
                            [2563, 1744],
                            [2625, 1726],
                            [2670, 1726],
                            [2706, 1735],
                            [2839, 1798],
                            [2857, 1824],
                            [2848, 1860],
                            [2821, 1878],
                            [2430, 2216],
                            [2412, 2269],
                            [2367, 2403],
                            [2243, 2474],
                            [1815, 2715],
                            [1646, 2777],
                            [1531, 2795],
                            [1762, 2893],
                            [1798, 2919],
                            [1878, 3026],
                            [2172, 2937],
                            [2189, 2893],
                            [2376, 2581],
                            [2608, 2376],
                            [2590, 2305],
                            [2554, 2287],
                            [2697, 2154],
                            [2750, 2154],
                            [2893, 2207],
                            [3053, 2056],
                            [3142, 1967],
                            [3275, 1842],
                            [3302, 1842],
                            [3293, 1798],
                            [3124, 1753],
                            [3142, 1691],
                            [3213, 1682],
                            [3293, 1655],
                            [3355, 1673],
                            [3364, 1718],
                            [2421, 2901],
                            [2554, 2652],
                            [2759, 2456],
                            [2928, 2314],
                            [2982, 2261],
                            [3017, 2225],
                            [3382, 2367],
                            [3444, 2376],
                            [3507, 2341],
                            [3160, 2100],
                            [3240, 2011],
                            [3302, 1967],
                            [3364, 1904],
                            [3382, 1869],
                            [3400, 1815],
                            [3427, 1691],
                            [3418, 1629],
                            [3516, 1682],
                            [3329, 2234],
                            [3409, 2136],
                            [3489, 2038],
                            [3551, 1967],
                            [3587, 1931],
                            [3649, 1860],
                            [3703, 1815],
                            [3783, 1718],
                            [3667, 1673],
                            [3845, 1629],
                            [3934, 2723],
                            [3898, 2777],
                            [3845, 2857],
                            [3800, 2919],
                            [4655, 1513],
                            [4780, 1370],
                            [4860, 1272],
                            [4726, 1086],
                            [4593, 943],
                            [4548, 934],
                            [4495, 943],
                            [4335, 1005],
                            [1361, 2732],
                            [1201, 2652],
                            [1121, 2652],
                            [925, 2572],
                            [756, 2501],
                            [721, 2394],
                            [649, 2367],
                            [1041, 2625],
                            [4780, 1370],
                            [4691, 1335],
                            [4611, 1317],
                            [4566, 1308],
                            [4513, 1290],
                            [4459, 1281],
                            [4397, 1272],
                            [4352, 1255],
                            [4281, 1228],
                            [4210, 1246],
                            [4094, 1237],
                            [4032, 1272],
                            [3970, 1299],
                            [3863, 1272],
                            [4726, 1290],
                            [4762, 1255],
                            [4726, 1219],
                            [4700, 1183],
                            [4673, 1157],
                            [4628, 1219],
                            [4566, 1166],
                            [4539, 1210],
                            [4513, 1210],
                            [4477, 1255],
                            [4851, 1290],
                            [4851, 1246],
                            [4806, 1192],
                            [4771, 1148],
                            [4878, 1130],
                            [4700, 1130],
                            [4717, 1086],
                            [4673, 1050],
                            [4530, 1059],
                            [4450, 1086],
                            [4388, 1148],
                            [4290, 1139],
                            [4228, 1166],
                            [4174, 1192],
                            [4691, 1228],
                            [4477, 1335],
                            [4361, 1317],
                            [4352, 1335],
                            [4326, 1281],
                            [4628, 1077], [2643, 329],
                            [2536, 240], [4397, 827], [4263, 810],
                            [3631, 2857], [3471, 2919], [3667, 2795],
                            [3525, 2741], [3436, 2777], [3329, 2750],
                            [2741, 445]]

        """
            Adding New Locations to the adj_list dictionary:

            1. Add the new location to the adj_list dictionary.
            2. open manage.py shell and run the following commands:
                from locations.management.commands.mapnav import handle_entry
                h= handle_entry().update()
                print(h.adj_list)
            3. It updates the database with the new location and gives the updated adj_list dictionary.
        """


        
        self.adj_list = {
    0: {
        "Hostel 12 Crown of the Campus": 6.425,
        "Hostel 14 Silicon Ship": 3.338,
        "H13 Night Canteen": 29.933,
        "Hostel 13 House of Titans": 29.933,
        "Mess for hostels 12 | 13 | 14": 2.378,
        1: 9.685,
        "Amul Parlour": 3.338,
    },
    "Amul Parlour": {0: 3.338},
    "Hostel 12 Crown of the Campus": {0: 6.425},
    "Hostel 14 Silicon Ship": {0: 3.338},
    "Hostel 13 House of Titans": {0: 29.933},
    "H13 Night Canteen": {0: 29.933},
    "Mess for hostels 12 | 13 | 14": {0: 2.378},
    1: {0: 9.685, 2: 6.481},
    2: {1: 6.481, 3: 4.293, 255: 325.184},
    "Security Check Point": {255: 2.125, 245: 15.101},
    3: {2: 4.293, 4: 25.717000000000002, 5: 10.333},
    4: {3: 25.717000000000002, "Hostel 06 Vikings": 5.569, "Type1 - 22": 9.125},
    "Type1 - 22": {4: 9.125},
    "Hostel 06 Vikings": {4: 5.569},
    5: {3: 10.333, 6: 6.977},
    6: {
        5: 6.977,
        7: 4.8340000000000005,
        "ATM - Canara Bank near H6": 1.9080000000000001,
    },
    "ATM - Canara Bank near H6": {6: 1.9080000000000001},
    7: {6: 4.8340000000000005, 8: 4.141},
    8: {7: 4.141, 9: 1.405, "Hostel 09 Nawaabon Ki Basti": 13.001},
    "Hostel 09 Nawaabon Ki Basti": {8: 13.001},
    9: {8: 1.405, 10: 13.474, 12: 7.993},
    10: {9: 13.474, 11: 21.8},
    11: {10: 21.8, "Hostel 18": 16.613},
    "Hostel 18": {11: 16.613},
    12: {9: 7.993, 13: 14.321, "Hostel 17": 5.994},
    "Hostel 17": {12: 5.994},
    13: {12: 14.321, 14: 3.098, 102: 11.584},
    14: {13: 3.098, 15: 32.53, "Chaayos Cafe": 1.458},
    "Chaayos Cafe": {14: 1.458},
    15: {14: 32.53, 16: 7.688, 17: 12.674},
    16: {15: 7.688, "Hostel 05 Penthouse": 18.549},
    "Hostel 05 Penthouse": {16: 18.549},
    17: {
        15: 12.674,
        18: 7.1290000000000004,
        "Tansa House King of campus (Proj. Staff Boys)": 11.425,
        "ATM - State Bank near Tansa": 9.316,
    },
    "ATM - State Bank near Tansa": {17: 9.316},
    "Tansa House King of campus (Proj. Staff Boys)": {17: 11.425},
    18: {17: 7.1290000000000004, 19: 5.78},
    19: {18: 5.78, 20: 4.293},
    20: {
        21: 40.441,
        19: 4.293,
        "Outdoor Sports Facility": 1.514,
        "Hostel 03 Vitruvians": 15.860000000000001,
    },
    "Outdoor Sports Facility": {20: 1.514},
    "Hostel 03 Vitruvians": {20: 15.860000000000001},
    21: {
        20: 40.441,
        22: 9.146,
        "Hostel 02 The Wild Ones": 25.09,
        "Indoor Stadium": 2.509,
        "Badminton Court": 2.509,
    },
    "Badminton Court": {21: 2.509},
    "Hostel 02 The Wild Ones": {21: 25.09},
    "Indoor Stadium": {21: 2.509},
    22: {21: 9.146, "Swimming Pool (new)": 5.345, 23: 5.365},
    "Swimming Pool (new)": {22: 5.345},
    23: {22: 5.365, 24: 12.52, 25: 10.333},
    24: {
        23: 12.52,
        "Students Activity Centre": 3.625,
        "New Yoga Room, SAC": 3.625,
        "Open Air Theatre": 3.625,
        "Film Room, SAC": 3.625,
    },
    "Film Room, SAC": {24: 3.625, 26: 7.621},
    "Open Air Theatre": {24: 3.625, 26: 7.621},
    "New Yoga Room, SAC": {24: 3.625, 26: 7.621},
    "Students Activity Centre": {24: 3.625, 26: 7.621},
    25: {23: 10.333, 26: 14.645, 27: 6.481},
    26: {
        25: 14.645,
        "Students Activity Centre": 7.621,
        "New Yoga Room, SAC": 7.621,
        "Open Air Theatre": 7.621,
        "Film Room, SAC": 7.621,
    },
    27: {
        25: 6.481,
        28: 7.696,
        "Hostel 01 Queen of the campus": 4.8340000000000005,
        "Aromas Canteen": 2.669,
    },
    "Hostel 01 Queen of the campus": {27: 4.8340000000000005, "Aromas Canteen": 13.973},
    28: {27: 7.696, "Domino's outlet": 4.034, 29: 2.612, "Aromas Canteen": 8.845},
    "Domino's outlet": {28: 4.034, 34: 2.089, "Aromas Canteen": 2.041},
    29: {28: 2.612, 30: 32.321, 34: 10.837},
    30: {29: 32.321, 31: 9.857, "Defence Research & Development Organization": 4.625},
    "Defence Research & Development Organization": {30: 4.625},
    31: {30: 9.857, 32: 16.354, 192: 13.573},
    32: {
        31: 16.354,
        "Hostel 15 Trident": 36.297000000000004,
        33: 28.409,
        "Hostel 15 Mess": 17992.225000000002,
    },
    "Hostel 15 Mess": {32: 17992.225000000002},
    "Hostel 15 Trident": {32: 36.297000000000004},
    33: {32: 28.409, "Hostel 16 Olympus": 19.721, "Hostel 16 Mess": 16594.448},
    "Hostel 16 Mess": {33: 16594.448},
    "Hostel 16 Olympus": {33: 19.721},
    34: {35: 3.133, 29: 10.837, "Domino's outlet": 2.089},
    35: {34: 3.133, 36: 5.14, 37: 49.652, 214: 0.388},
    36: {35: 5.14, "State Bank of India Branch": 1.682, 94: 21.533},
    "State Bank of India Branch": {36: 1.682},
    37: {35: 49.652, 38: 37.885, 95: 128.321},
    38: {37: 37.885, 39: 9.928, "Central Library": 1.217},
    "Central Library": {38: 1.217, 40: 7.625},
    39: {38: 9.928, 40: 12.962, 89: 28.409, 90: 5.994},
    40: {39: 12.962, 41: 1.0, "Central Library": 7.625},
    41: {40: 1.0, 42: 1.296, 180: 5.184},
    42: {
        41: 1.296,
        43: 5.365,
        "Mathematics Department": 5.93,
        "Old Software Lab": 5.93,
        "Inter-disciplinary Programme in Educational Technology": 5.93,
        "Centre for Formal Design and Verification of Software": 5.93,
        "Centre for Distance Engineering Education Programme": 5.93,
    },
    "Centre for Distance Engineering Education Programme": {42: 5.93},
    "Centre for Formal Design and Verification of Software": {42: 5.93},
    "Inter-disciplinary Programme in Educational Technology": {42: 5.93},
    "Mathematics Department": {42: 5.93},
    "Old Software Lab": {42: 5.93},
    43: {
        42: 5.365,
        44: 4.168,
        "Old Computer Science Engineering Department": 3.4,
        "New Software Lab": 3.4,
        "Centre for Technology Alternatives for Rural Areas": 3.4,
    },
    "Centre for Technology Alternatives for Rural Areas": {43: 3.4},
    "New Software Lab": {43: 3.4},
    "Old Computer Science Engineering Department": {43: 3.4},
    44: {43: 4.168, 45: 1.377, 89: 16.004},
    45: {44: 1.377, 46: 6.724, 47: 9.685, "Fluid Mechanics and Fluid Power Lab": 0.389},
    "Fluid Mechanics and Fluid Power Lab": {45: 0.389},
    46: {45: 6.724, 47: 1.053, 48: 4.133, "ENELEK Power Sine": 0.9},
    "ENELEK Power Sine": {46: 0.9},
    47: {45: 9.685, 46: 1.053},
    48: {
        46: 4.133,
        49: 4.698,
        "Tinkerers Lab": 1.1380000000000001,
        "Refrigeration, A/C and Cryogenics Lab": 1.1380000000000001,
        "Treelabs": 1.1380000000000001,
        "N3 Bay": 28.288,
    },
    "Treelabs": {48: 1.1380000000000001},
    "Refrigeration, A/C and Cryogenics Lab": {48: 1.1380000000000001},
    "Tinkerers Lab": {48: 1.1380000000000001},
    49: {
        48: 4.698,
        50: 11.441,
        "Mechanical Engineering Department": 27.361,
        "Industrial Engineering and Operations Research": 27.361,
    },
    "Industrial Engineering and Operations Research": {49: 27.361},
    "Mechanical Engineering Department": {49: 27.361},
    50: {49: 11.441, 51: 2.997, 52: 1.549},
    51: {
        50: 2.997,
        76: 23.297,
        "Industrial Design Centre": 5.002,
        "IDC Canteen": 5.002,
        "IDC Shakti": 5.002,
    },
    "IDC Shakti": {51: 5.002},
    "IDC Canteen": {51: 5.002},
    "Industrial Design Centre": {51: 5.002},
    52: {50: 1.549, 53: 5.869, 76: 49.213, 178: 82.57600000000001},
    53: {
        52: 5.869,
        54: 21.053,
        "Civil Engineering Department": 21.361,
        "Victor Menezes Convention Centre": 9.385,
        "Centre for Urban Science and Engineering (inside civil)": 21.361,
        "Inter-disciplinary Programme in Climate Studies": 21.361,
    },
    "Inter-disciplinary Programme in Climate Studies": {53: 21.361},
    "Centre for Urban Science and Engineering (inside civil)": {53: 21.361},
    "Civil Engineering Department": {53: 21.361},
    "Victor Menezes Convention Centre": {53: 9.385},
    54: {
        53: 21.053,
        55: 3.872,
        "Electrical Engineering Department": 22.985,
        "Electrical Engineering Annexe Building": 1.156,
    },
    "Electrical Engineering Department": {54: 22.985, 176: 18.761, 56: 4.453},
    "Electrical Engineering Annexe Building": {54: 1.156, 56: 35.746},
    55: {54: 3.872, 56: 18.434, 57: 4.212},
    56: {
        55: 18.434,
        "Girish Gaitonde Building": 6.682,
        "Electrical Engineering Department": 4.453,
        "Electrical Engineering Annexe Building": 35.746,
    },
    "Girish Gaitonde Building": {175: 6.597, 56: 6.682},
    57: {
        174: 90.82900000000001,
        55: 4.212,
        58: 4.745,
        "Seminar Hall": 3.536,
        "Rock Powdering Lab": 8.125,
        "Rock Cutting Lab": 8.125,
    },
    "Seminar Hall": {57: 3.536},
    "Rock Cutting Lab": {57: 8.125},
    "Rock Powdering Lab": {57: 8.125},
    58: {
        57: 4.745,
        59: 15.842,
        "Metallurgical Engineering and Material Science Department": 31.397000000000002,
        "Corrosion Science Paint Lab": 31.397000000000002,
        "Corrosion Lab 1": 31.397000000000002,
        "Humanities and Social Sciences Department": 16.97,
        "Aerospace Engineering Annexe": 16.97,
        "Inter-disciplinary Programme in Corrosion Science & Engineering": 31.397000000000002,
        "Aqueous Corrosion Lab": 31.397000000000002,
    },
    "Aqueous Corrosion Lab": {58: 31.397000000000002, 173: 20.2},
    "Inter-disciplinary Programme in Corrosion Science & Engineering": {
        58: 31.397000000000002,
        173: 20.2,
    },
    "Metallurgical Engineering and Material Science Department": {
        58: 31.397000000000002,
        173: 20.2,
    },
    "Corrosion Lab 1": {58: 31.397000000000002, 173: 20.2},
    "Corrosion Science Paint Lab": {58: 31.397000000000002, 173: 20.2},
    "Humanities and Social Sciences Department": {58: 16.97},
    "Aerospace Engineering Annexe": {58: 16.97},
    59: {
        58: 15.842,
        60: 14.482000000000001,
        "Lecture Hall Complex - 1 & 2": 20.714000000000002,
        "LT 001": 20.714000000000002,
        "LT 002": 20.714000000000002,
        "LT 003": 20.714000000000002,
        "LT 004": 20.714000000000002,
        "LT 005": 20.714000000000002,
        "LT 006": 20.714000000000002,
        "LT 101": 20.714000000000002,
        "LT 102": 20.714000000000002,
        "LT 103": 20.714000000000002,
        "LT 104": 20.714000000000002,
        "LT 105": 20.714000000000002,
        "LT 106": 20.714000000000002,
        "LT 201": 20.714000000000002,
        "LT 202": 20.714000000000002,
        "LT 203": 20.714000000000002,
        "LT 204": 20.714000000000002,
        "LT 205": 20.714000000000002,
        "LT 206": 20.714000000000002,
        "LT 301": 20.714000000000002,
        "LT 302": 20.714000000000002,
        "LT 303": 20.714000000000002,
        "LT 304": 20.714000000000002,
        "LT 305": 20.714000000000002,
        "LT 306": 20.714000000000002,
        "LC 001": 20.714000000000002,
        "LC 002": 20.714000000000002,
        "LC 101": 20.714000000000002,
        "LC 102": 20.714000000000002,
        "LC 201": 20.714000000000002,
        "LC 202": 20.714000000000002,
        "LC 301": 20.714000000000002,
        "LC 302": 20.714000000000002,
        "LH 101": 20.714000000000002,
        "LH 102": 20.714000000000002,
        "LH 301": 20.714000000000002,
        "LH 302": 20.714000000000002,
        "LA 001": 5.945,
        "LA 002": 5.945,
        "LA 201": 5.945,
        "LA 202": 5.945,
        "Lecture Hall Complex - 3": 5.945,
        "WRCBB Wadhwani Research Centre in Biosciences and Bioengineering ": 54.517,
        "Biosciences and Bioengineering Department": 54.517,
    },
    "Biosciences and Bioengineering Department": {59: 54.517},
    "WRCBB Wadhwani Research Centre in Biosciences and Bioengineering ": {59: 54.517},
    "LH 302": {59: 20.714000000000002, 172: 26.177},
    "LH 301": {59: 20.714000000000002, 172: 26.177},
    "LH 102": {59: 20.714000000000002, 172: 26.177},
    "LH 101": {59: 20.714000000000002, 172: 26.177},
    "LC 302": {59: 20.714000000000002, 172: 26.177},
    "LC 301": {59: 20.714000000000002, 172: 26.177},
    "LC 202": {59: 20.714000000000002, 172: 26.177},
    "LC 201": {59: 20.714000000000002, 172: 26.177},
    "LC 102": {59: 20.714000000000002, 172: 26.177},
    "LC 101": {59: 20.714000000000002, 172: 26.177},
    "LC 002": {59: 20.714000000000002, 172: 26.177},
    "LC 001": {59: 20.714000000000002, 172: 26.177},
    "LT 001": {59: 20.714000000000002, 172: 26.177},
    "LT 306": {59: 20.714000000000002, 172: 26.177},
    "LT 305": {59: 20.714000000000002, 172: 26.177},
    "LT 304": {59: 20.714000000000002, 172: 26.177},
    "LT 303": {59: 20.714000000000002, 172: 26.177},
    "LT 302": {59: 20.714000000000002, 172: 26.177},
    "LT 301": {59: 20.714000000000002, 172: 26.177},
    "LT 206": {59: 20.714000000000002, 172: 26.177},
    "LT 205": {59: 20.714000000000002, 172: 26.177},
    "LT 204": {59: 20.714000000000002, 172: 26.177},
    "LT 203": {59: 20.714000000000002, 172: 26.177},
    "LT 202": {59: 20.714000000000002, 172: 26.177},
    "LT 201": {59: 20.714000000000002, 172: 26.177},
    "LT 106": {59: 20.714000000000002, 172: 26.177},
    "LT 105": {59: 20.714000000000002, 172: 26.177},
    "LT 104": {59: 20.714000000000002, 172: 26.177},
    "LT 103": {59: 20.714000000000002, 172: 26.177},
    "LT 102": {59: 20.714000000000002, 172: 26.177},
    "LT 101": {59: 20.714000000000002, 172: 26.177},
    "LT 006": {59: 20.714000000000002, 172: 26.177},
    "LT 005": {59: 20.714000000000002, 172: 26.177},
    "LT 004": {59: 20.714000000000002, 172: 26.177},
    "LT 003": {59: 20.714000000000002, 172: 26.177},
    "LT 002": {59: 20.714000000000002, 172: 26.177},
    "Lecture Hall Complex - 1 & 2": {59: 20.714000000000002, 172: 26.177},
    "LA 202": {59: 5.945},
    "LA 201": {59: 5.945},
    "LA 002": {59: 5.945},
    "LA 001": {59: 5.945},
    "Lecture Hall Complex - 3": {59: 5.945},
    60: {
        59: 14.482000000000001,
        61: 4.141,
        "Physics Department": 22.85,
        "Chemical Engineering Department": 30.472,
        "Chemistry Department": 30.472,
    },
    "Physics Department": {60: 22.85, 171: 22.669},
    "Chemistry Department": {60: 30.472, 67: 79.88},
    "Chemical Engineering Department": {60: 30.472, 67: 79.88},
    61: {60: 4.141, 62: 3.872, 161: 6.481},
    62: {61: 3.872, 63: 2.809},
    63: {62: 2.809, 64: 174.113, 160: 40.01},
    64: {63: 174.113, 65: 6.6530000000000005, 181: 25.61},
    65: {
        64: 6.6530000000000005,
        66: 4.212,
        "DESE & CESE New Building": 13.13,
        "Cafe Coffee Day": 14.152000000000001,
        "Energy Science and Engineering (New Building)": 13.13,
    },
    "Energy Science and Engineering (New Building)": {65: 13.13},
    "DESE & CESE New Building": {65: 13.13},
    "Cafe Coffee Day": {65: 14.152000000000001},
    66: {65: 4.212, 67: 4.168, 70: 165.841},
    67: {
        66: 4.168,
        68: 60.826,
        "Chemical Engineering Department": 79.88,
        "Chemistry Department": 79.88,
    },
    68: {
        67: 60.826,
        69: 19.856,
        "Aerospace Engineering Department": 2.448,
        "Centre for Aerospace Systems Design and Engineering": 2.448,
    },
    "Centre for Aerospace Systems Design and Engineering": {68: 2.448},
    "Aerospace Engineering Department": {68: 2.448},
    69: {68: 19.856, "ONGC Research Centre": 2.498, 71: 5.994},
    "ONGC Research Centre": {69: 2.498},
    70: {
        66: 165.841,
        71: 2.089,
        "Proposed Building for Tata Centre for Technology": 10.585,
        "Proposed NCAIR": 10.585,
        "Proposed Bio Mechanical Department": 10.585,
        "Proposed D.S Foundation": 10.585,
        "Proposed Press ": 10.585,
    },
    "Proposed Press ": {70: 10.585},
    "Proposed D.S Foundation": {70: 10.585},
    "Proposed Bio Mechanical Department": {70: 10.585},
    "Proposed NCAIR": {70: 10.585},
    "Proposed Building for Tata Centre for Technology": {70: 10.585},
    71: {70: 2.089, 72: 21.674, 69: 5.994},
    72: {71: 21.674, 73: 3.133, "Energy Science and Engineering": 2.813},
    "Energy Science and Engineering": {72: 2.813},
    73: {72: 3.133, 74: 0.81, "Earth Science Department": 17.876},
    "Earth Science Department": {73: 17.876},
    74: {
        73: 0.81,
        75: 8.885,
        "Centre of Studies in Resources Engineering": 4.45,
        "Society for Innovation and Entrepreneurship": 4.45,
    },
    "Society for Innovation and Entrepreneurship": {74: 4.45},
    "Centre of Studies in Resources Engineering": {74: 4.45},
    75: {
        74: 8.885,
        76: 10.73,
        "Centre for Environmental Science and Engineering": 15.937000000000001,
    },
    "Centre for Environmental Science and Engineering": {75: 15.937000000000001},
    76: {
        75: 10.73,
        51: 23.297,
        52: 49.213,
        77: 4.8340000000000005,
        "Non- Academic Staff Association": 4.212,
        "Printing Press": 4.212,
    },
    "Printing Press": {76: 4.212},
    "Non- Academic Staff Association": {76: 4.212},
    77: {
        76: 4.8340000000000005,
        78: 24.026,
        "Structural integrity Testing and Analysis Centre": 4.6930000000000005,
        "S3 Bay": 7.633,
    },
    "S3 Bay": {77: 7.633},
    "Structural integrity Testing and Analysis Centre": {
        77: 4.6930000000000005,
        82: 44.285000000000004,
    },
    78: {
        77: 24.026,
        79: 19.37,
        "Electrical Maintenence": 5.92,
        "Machine Tool Lab": 13.768,
    },
    "Machine Tool Lab": {79: 21.634, 78: 13.768},
    "Electrical Maintenence": {78: 5.92},
    79: {
        78: 19.37,
        80: 11.765,
        "Machine Tool Lab": 21.634,
        "OrthoCad Lab": 8.593,
        "Micro Fluidics Lab": 6.273,
        "RM Lab (Rapid manufacturing)": 9.133000000000001,
        "S1 Bay": 5.114,
        "N1 Bay": 4.049,
        "Supercritical fluid Processing facility (Chemical Engg.)": 5.114,
        "S2 Bay": 21.634,
        "UG Lab / S2 Bay": 21.634,
        "Fuel Cell Research Facility": 4.049,
    },
    "Fuel Cell Research Facility": {79: 4.049, 80: 9.992, 82: 4.905},
    "UG Lab / S2 Bay": {79: 21.634},
    "S2 Bay": {79: 21.634},
    "Supercritical fluid Processing facility (Chemical Engg.)": {79: 5.114},
    "N1 Bay": {79: 4.049},
    "S1 Bay": {79: 5.114},
    "RM Lab (Rapid manufacturing)": {79: 9.133000000000001},
    "OrthoCad Lab": {79: 8.593},
    "Micro Fluidics Lab": {79: 6.273},
    80: {
        79: 11.765,
        81: 5.7170000000000005,
        82: 12.461,
        "Fuel Cell Research Facility": 9.992,
    },
    81: {
        185: 7.688,
        80: 5.7170000000000005,
        "Physics Lab (Ist Years)": 1.289,
        "UG Lab (1st years)": 1.289,
        "Power House": 6.309,
    },
    "UG Lab (1st years)": {81: 1.289, 82: 10.225},
    "Physics Lab (Ist Years)": {81: 1.289, 82: 10.225},
    "Power House": {81: 6.309},
    82: {
        80: 12.461,
        83: 11.773,
        "UG Lab (1st years)": 10.225,
        "Physics Lab (Ist Years)": 10.225,
        "Structural integrity Testing and Analysis Centre": 44.285000000000004,
        "Fuel Cell Research Facility": 4.905,
    },
    83: {
        82: 11.773,
        84: 3.321,
        "SMAmL Suman Mashruwala Advanced Microengineering Lab": 1.109,
        "Thermal Hydraulic Test Facility": 6.498,
        "N2 Bay": 7.297,
        "N3 Bay": 4.82,
    },
    "N3 Bay": {48: 28.288, 83: 4.82},
    "N2 Bay": {83: 7.297},
    "SMAmL Suman Mashruwala Advanced Microengineering Lab": {83: 1.109},
    "Thermal Hydraulic Test Facility": {83: 6.498},
    84: {
        83: 3.321,
        85: 18.914,
        "Cummins Engine Research facility": 0.65,
        "Heat Transfer and Thermodynamic Lab": 0.89,
        "Steam Power Lab": 1.186,
        "IC Engine and Combustion Lab": 4.525,
    },
    "IC Engine and Combustion Lab": {84: 4.525, 85: 6.793},
    "Steam Power Lab": {84: 1.186},
    "Cummins Engine Research facility": {84: 0.65},
    "Heat Transfer and Thermodynamic Lab": {84: 0.89},
    85: {
        84: 18.914,
        88: 6.724,
        86: 11.765,
        "Metal Forming Lab": 6.548,
        "Old ONGC Lab": 3.298,
        "Structural Evaluation & Material Technologies Lab": 2.848,
        "Heavy Structure Lab": 11.133000000000001,
        "Hydraulics Lab": 1.193,
        "Concrete Technology Lab": 11.133000000000001,
        "IC Engine and Combustion Lab": 6.793,
    },
    "Concrete Technology Lab": {85: 11.133000000000001},
    "Hydraulics Lab": {85: 1.193, 88: 4.6850000000000005},
    "Heavy Structure Lab": {85: 11.133000000000001},
    "Structural Evaluation & Material Technologies Lab": {85: 2.848},
    "Old ONGC Lab": {85: 3.298},
    86: {
        85: 11.765,
        87: 5.041,
        "Geotechnical Engg. Lab": 0.164,
        "Metal Forming Lab": 1.369,
    },
    "Metal Forming Lab": {86: 1.369, 85: 6.548},
    "Geotechnical Engg. Lab": {86: 0.164},
    87: {
        86: 5.041,
        "National Geotechnical Centrifuge Facility": 1.5250000000000001,
        "Vihar House": 38.825,
        "GMFL Lab / Geophysical and multiphase Flows Lab": 31.265,
    },
    "GMFL Lab / Geophysical and multiphase Flows Lab": {87: 31.265},
    "Vihar House": {87: 38.825},
    "National Geotechnical Centrifuge Facility": {87: 1.5250000000000001},
    88: {
        85: 6.724,
        "Solar Lab": 11.485,
        89: 2.997,
        "Heat Pump Lab": 1.25,
        "Hydraulics Lab Workshop": 3.94,
        "Hydraulics Lab": 4.6850000000000005,
        "Hydraulics Lab (New)": 1.885,
    },
    "Hydraulics Lab (New)": {88: 1.885, 89: 1.156},
    "Hydraulics Lab Workshop": {88: 3.94},
    "Solar Lab": {88: 11.485},
    "Heat Pump Lab": {88: 1.25},
    89: {44: 16.004, 88: 2.997, 39: 28.409, "Hydraulics Lab (New)": 1.156},
    90: {
        91: 7.8500000000000005,
        39: 5.994,
        "Inter-disciplinary Programme in Systems and Control Engineering": 2.048,
    },
    "Inter-disciplinary Programme in Systems and Control Engineering": {90: 2.048},
    91: {
        90: 7.8500000000000005,
        92: 3.5380000000000003,
        "NanoTech. & Science Research Centre": 3.697,
        "Advanced Centre for Research in Electronics": 3.697,
        "Sophisticated Analytical Instruments Facility": 3.697,
    },
    "Sophisticated Analytical Instruments Facility": {91: 3.697},
    "Advanced Centre for Research in Electronics": {91: 3.697},
    "NanoTech. & Science Research Centre": {91: 3.697},
    92: {91: 3.5380000000000003, 93: 9.146, 211: 1.549, 213: 9.857, 212: 1.018},
    93: {92: 9.146, 94: 2.916, 213: 0.081},
    94: {93: 2.916, 213: 2.997, 214: 3.133, 36: 21.533},
    95: {96: 5.994, 169: 17.525000000000002, 37: 128.321},
    96: {95: 5.994, "NCC Office": 18.866, 97: 21.146, "Squash Court": 22.802},
    "Squash Court": {96: 22.802, 97: 9.040000000000001},
    "NCC Office": {96: 18.866},
    97: {
        96: 21.146,
        98: 11.441,
        "Staff Hostel": 83.46600000000001,
        "Squash Court": 9.040000000000001,
    },
    "Staff Hostel": {97: 83.46600000000001},
    98: {
        97: 11.441,
        99: 3.133,
        101: 6.885,
        "Hostel 11 Athena (Girls Hostel)": 8.82,
        "Printing and photocopying H11": 8.82,
    },
    "Printing and photocopying H11": {98: 8.82},
    "Hostel 11 Athena (Girls Hostel)": {98: 8.82},
    99: {98: 3.133, 100: 6.977, "Basketball Court": 2.269},
    "Basketball Court": {99: 2.269},
    100: {99: 6.977, "Hockey Ground": 22.48, "Gymkhana Grounds": 9.901},
    "Hockey Ground": {100: 22.48},
    "Gymkhana Grounds": {100: 9.901},
    101: {98: 6.885, 102: 28.925, "Gymkhana Building": 3.725, "Brewberrys Cafe": 1.682},
    "Gymkhana Building": {101: 3.725},
    "Brewberrys Cafe": {101: 1.682},
    102: {101: 28.925, 13: 11.584, 103: 53.573},
    103: {102: 53.573, 104: 3.872},
    104: {103: 3.872, 105: 2.997},
    105: {104: 2.997, 106: 51.872},
    106: {105: 51.872, 107: 2.873},
    107: {106: 2.873, 108: 2.314},
    108: {107: 2.314, 109: 3.592},
    109: {108: 3.592, 110: 12.745000000000001},
    110: {109: 12.745000000000001, 111: 2.225},
    111: {110: 2.225, 112: 12.674, 115: 1.549},
    112: {111: 12.674, 113: 11.449},
    113: {112: 11.449, 114: 42.754},
    114: {113: 42.754, "Boat House": 23.722},
    "Boat House": {114: 23.722},
    115: {111: 1.549, 116: 4.168},
    116: {115: 4.168, 117: 2.025},
    117: {116: 2.025, 118: 1.377},
    118: {117: 1.377, 119: 21.658},
    119: {118: 21.658, 120: 1.0},
    120: {119: 1.0, 121: 1.377},
    121: {120: 1.377, 122: 1.053, "National Centre for Mathematics": 2.164},
    122: {121: 1.053, 123: 267.125, "Guest House/Padmavihar": 11484.925000000001},
    "Guest House/Padmavihar": {122: 11484.925000000001},
    "National Centre for Mathematics": {121: 2.164},
    123: {
        122: 267.125,
        124: 3.133,
        138: 20.417,
        "Type B-14": 7.2250000000000005,
        "Guest House / Jalvihar": 38.484,
    },
    "Guest House / Jalvihar": {123: 38.484},
    "Type B-14": {123: 7.2250000000000005},
    124: {123: 3.133, 125: 19.981},
    125: {124: 19.981, 126: 20.417},
    126: {125: 20.417, 127: 241.26500000000001, 135: 29.138, "Type B-13": 12.785},
    "Type B-13": {126: 12.785},
    127: {126: 241.26500000000001, 128: 32.405, "Proposed TypeA Building": 20.89},
    "Proposed TypeA Building": {127: 20.89},
    128: {127: 32.405, 129: 13.549},
    129: {
        128: 13.549,
        130: 62.965,
        193: 32.869,
        "B 19 Old Multistoried Building- Residence ": 22.024,
    },
    "B 19 Old Multistoried Building- Residence ": {129: 22.024},
    130: {129: 62.965, 131: 1.972, "White House": 30.445},
    "White House": {130: 30.445},
    131: {130: 1.972, 132: 17.849, "CTR 20": 4.001},
    "CTR 20": {131: 4.001},
    132: {131: 17.849, 133: 94.357, "CTR 19": 4.165, "Bungalow A10 ": 16.66},
    "Bungalow A10 ": {132: 16.66, 133: 44.181},
    "CTR 19": {132: 4.165},
    133: {
        132: 94.357,
        134: 2.225,
        "Bungalow A11 ": 12.308,
        "Bungalow A10 ": 44.181,
        "Bungalow A8 ": 39.22,
    },
    "Bungalow A8 ": {133: 39.22, 153: 114.781},
    134: {
        133: 2.225,
        135: 132.31300000000002,
        153: 53.888,
        "Shishu Vihar": 18.405,
        "Bungalow A5 ": 18.925,
        "Bungalow A11 ": 13.289,
    },
    "Bungalow A11 ": {133: 12.308, 134: 13.289},
    "Bungalow A5 ": {134: 18.925, 153: 13.213000000000001},
    "Shishu Vihar": {134: 18.405, 153: 13.109},
    135: {
        134: 132.31300000000002,
        136: 95.849,
        126: 29.138,
        "A1 Director Bungalow": 54.92,
    },
    "A1 Director Bungalow": {
        135: 54.92,
        136: 14.357000000000001,
        155: 28.746000000000002,
        154: 26.249,
    },
    136: {
        135: 95.849,
        137: 5.365,
        155: 29.201,
        "Type B-1": 5.248,
        "Bungalow A13 ": 5.188,
        "A1 Director Bungalow": 14.357000000000001,
    },
    "Bungalow A13 ": {136: 5.188},
    "Type B-1": {136: 5.248},
    137: {136: 5.365, 138: 1.62},
    138: {137: 1.62, 139: 38.138, 123: 20.417},
    139: {138: 38.138, 140: 2.809},
    140: {139: 2.809, 141: 23.258},
    141: {140: 23.258, 142: 48.401, 157: 10.837, "Guest House/Vanvihar": 13240.298},
    "Guest House/Vanvihar": {141: 13240.298},
    142: {
        141: 48.401,
        143: 15.842,
        162: 13.385,
        "Gulmohar Garden Cafetaria": 5.6450000000000005,
        "Staff Club": 15.725,
    },
    "Staff Club": {142: 15.725},
    143: {142: 15.842, 144: 33.314, "Hospital": 17.876},
    "Hospital": {143: 17.876},
    144: {143: 33.314, 145: 0.729, 166: 12.178},
    145: {144: 0.729, 146: 2.017},
    146: {145: 2.017, 147: 30.586000000000002, 152: 11.441},
    147: {146: 30.586000000000002, 148: 4.168, "Kshitij Udyan": 23.490000000000002},
    "Kshitij Udyan": {147: 23.490000000000002},
    148: {147: 4.168, 149: 5.122},
    149: {148: 5.122, 150: 7.1290000000000004, "Tennis Court (new)": 56.45},
    "Tennis Court (new)": {149: 56.45},
    150: {149: 7.1290000000000004, 151: 4.168},
    151: {152: 2.106, 150: 4.168, 169: 5.905},
    152: {
        151: 2.106,
        168: 4.698,
        146: 11.441,
        "Convocation Hall": 11.93,
        "Institute Music Room": 11.93,
    },
    "Institute Music Room": {152: 11.93},
    "Convocation Hall": {152: 11.93},
    153: {
        134: 53.888,
        154: 79.69,
        "Main Gate no. 2": 139.14000000000001,
        "Shishu Vihar": 13.109,
        "Bungalow A5 ": 13.213000000000001,
        "ATM - State Bank Main Gate": 172.32500000000002,
        "Bungalow A8 ": 114.781,
    },
    "ATM - State Bank Main Gate": {153: 172.32500000000002},
    "Main Gate no. 2": {153: 139.14000000000001},
    154: {153: 79.69, 155: 80.441, "A1 Director Bungalow": 26.249},
    155: {
        136: 29.201,
        154: 80.441,
        156: 48.725,
        "Hostel 10 Annexe (Girls Hostel)": 16.145,
        "A1 Director Bungalow": 28.746000000000002,
    },
    "Hostel 10 Annexe (Girls Hostel)": {155: 16.145},
    156: {
        155: 48.725,
        157: 5.7250000000000005,
        "Hostel 10 Phoenix (Girls Hostel)": 6.713,
    },
    "Hostel 10 Phoenix (Girls Hostel)": {156: 6.713},
    157: {156: 5.7250000000000005, 158: 2.521, 141: 10.837},
    158: {
        157: 2.521,
        162: 36.074,
        159: 153.389,
        "Gulmohar Building": 5.825,
        "Gulmohar Garden Cafetaria": 9.554,
        "ATM - Canara Bank near Gulmohar": 5.825,
        "Gulmohar Restaurant": 5.825,
    },
    "Gulmohar Restaurant": {158: 5.825},
    "ATM - Canara Bank near Gulmohar": {158: 5.825},
    "Gulmohar Garden Cafetaria": {162: 15.3, 142: 5.6450000000000005, 158: 9.554},
    "Gulmohar Building": {158: 5.825},
    159: {158: 153.389, 160: 3.9250000000000003, 171: 20.498},
    160: {159: 3.9250000000000003, 161: 5.194, 63: 40.01, 253: 160.865},
    161: {160: 5.194, 61: 6.481},
    162: {142: 13.385, 158: 36.074, 163: 14.321, "Gulmohar Garden Cafetaria": 15.3},
    163: {
        162: 14.321,
        164: 5.78,
        "Faqir Chand Kohli Auditorium": 12.746,
        "Kanwal Rekhi School of Information Technology": 12.746,
        "KReSIT Canteen": 12.746,
    },
    "KReSIT Canteen": {163: 12.746, 172: 12.564},
    "Kanwal Rekhi School of Information Technology": {163: 12.746, 172: 12.564},
    "Faqir Chand Kohli Auditorium": {163: 12.746, 172: 12.564},
    "Computer Centre": {164: 397.8, 173: 197.93},
    164: {163: 5.78, 165: 7.813, "Computer Centre": 397.8},
    165: {164: 7.813, 166: 1.549, 174: 38.938},
    166: {
        165: 1.549,
        167: 3.24,
        144: 12.178,
        "School of Management": 15.133000000000001,
        "Industrial Research & Consultancy Centre": 15.133000000000001,
    },
    "Industrial Research & Consultancy Centre": {175: 10.82, 166: 15.133000000000001},
    "School of Management": {175: 10.82, 166: 15.133000000000001},
    167: {166: 3.24, 168: 16.105},
    168: {167: 16.105, 152: 4.698, 169: 3.9250000000000003, 170: 8.002},
    169: {168: 3.9250000000000003, 95: 17.525000000000002, 151: 5.905},
    170: {
        168: 8.002,
        "Main Building": 14.308,
        "Joint Admission Test for M.Sc. Office": 14.308,
        "Printing and photocopying Main Building": 14.308,
        "Hostel Coordinating Unit": 14.308,
    },
    "Hostel Coordinating Unit": {170: 14.308, 179: 2.61},
    "Printing and photocopying Main Building": {170: 14.308, 179: 2.61},
    "Joint Admission Test for M.Sc. Office": {170: 14.308, 179: 2.61},
    "Main Building": {170: 14.308, 179: 2.61},
    171: {172: 16.004, 159: 20.498, "Physics Department": 22.669},
    172: {
        171: 16.004,
        173: 16.004,
        "Kanwal Rekhi School of Information Technology": 12.564,
        "KReSIT Canteen": 12.564,
        "Faqir Chand Kohli Auditorium": 12.564,
        "Lecture Hall Complex - 1 & 2": 26.177,
        "LT 001": 26.177,
        "LT 002": 26.177,
        "LT 003": 26.177,
        "LT 004": 26.177,
        "LT 005": 26.177,
        "LT 006": 26.177,
        "LT 101": 26.177,
        "LT 102": 26.177,
        "LT 103": 26.177,
        "LT 104": 26.177,
        "LT 105": 26.177,
        "LT 106": 26.177,
        "LT 201": 26.177,
        "LT 202": 26.177,
        "LT 203": 26.177,
        "LT 204": 26.177,
        "LT 205": 26.177,
        "LT 206": 26.177,
        "LT 301": 26.177,
        "LT 302": 26.177,
        "LT 303": 26.177,
        "LT 304": 26.177,
        "LT 305": 26.177,
        "LT 306": 26.177,
        "LC 001": 26.177,
        "LC 002": 26.177,
        "LC 101": 26.177,
        "LC 102": 26.177,
        "LC 201": 26.177,
        "LC 202": 26.177,
        "LC 301": 26.177,
        "LC 302": 26.177,
        "LH 101": 26.177,
        "LH 102": 26.177,
        "LH 301": 26.177,
        "LH 302": 26.177,
    },
    173: {
        172: 16.004,
        174: 8.885,
        "Computer Centre": 197.93,
        "Metallurgical Engineering and Material Science Department": 20.2,
        "Corrosion Science Paint Lab": 20.2,
        "Corrosion Lab 1": 20.2,
        "Inter-disciplinary Programme in Corrosion Science & Engineering": 20.2,
        "Aqueous Corrosion Lab": 20.2,
    },
    174: {173: 8.885, 175: 2.592, 165: 38.938, 57: 90.82900000000001},
    175: {
        174: 2.592,
        176: 8.885,
        "Girish Gaitonde Building": 6.597,
        "School of Management": 10.82,
        "Industrial Research & Consultancy Centre": 10.82,
    },
    176: {
        175: 8.885,
        177: 4.941,
        "Electrical Engineering Department": 18.761,
        "Cafe 92": 2.521,
    },
    "Cafe 92": {176: 2.521},
    177: {
        176: 4.941,
        178: 15.809000000000001,
        "PC Saxena Auditorium / Lecture Theatre": 3.65,
    },
    "PC Saxena Auditorium / Lecture Theatre": {177: 3.65},
    178: {179: 15.481, 177: 15.809000000000001, 52: 82.57600000000001, 180: 11.765},
    179: {
        178: 15.481,
        "Main Building": 2.61,
        "Joint Admission Test for M.Sc. Office": 2.61,
        "Printing and photocopying Main Building": 2.61,
        "Hostel Coordinating Unit": 2.61,
    },
    180: {41: 5.184, 178: 11.765},
    181: {64: 25.61, 182: 4.212, "Kendriya Vidyalaya ": 2.682},
    "Kendriya Vidyalaya ": {181: 2.682},
    182: {181: 4.212, 183: 9.209, "Medical Store": 11.365, "Uphar": 25.16},
    "Medical Store": {182: 11.365},
    "Uphar": {182: 25.16},
    183: {184: 5.869, 182: 9.209, "Post Office": 5.45},
    "Post Office": {183: 5.45},
    184: {183: 5.869, "Market Gate, Y point Gate no. 3": 3.65, 249: 32.405},
    "Market Gate, Y point Gate no. 3": {184: 3.65},
    185: {81: 7.688, 186: 36.074, "Hostel 10A QIP (Girls Hostel)": 7.946},
    "Hostel 10A QIP (Girls Hostel)": {185: 7.946},
    186: {185: 36.074, 187: 16.004, 201: 0.0},
    187: {186: 16.004, 226: 0.757, 225: 0.405, "QIP 2": 3.217},
    "QIP 2": {225: 1.768, 187: 3.217},
    188: {189: 38.138, "K-Yantra Lab (CSE Dept.)": 5.057, 231: 0.081, 228: 5.869},
    "K-Yantra Lab (CSE Dept.)": {231: 6.29, 188: 5.057},
    189: {188: 38.138, 190: 2.106, 232: 17.849, "Tulsi B": 2.336, "B 22 Ananta": 19.54},
    "B 22 Ananta": {189: 19.54},
    "Tulsi B": {189: 2.336},
    190: {189: 2.106, 191: 2.89, "Tulsi A": 1.413, "Sameer Hill": 146.605},
    "Sameer Hill": {190: 146.605},
    "Tulsi A": {190: 1.413},
    191: {
        190: 2.89,
        192: 29.444,
        "B 23 Aravali": 6.449,
        "Society for Applied Microwave Electronics Engineering & Research": 13.085,
    },
    "Society for Applied Microwave Electronics Engineering & Research": {191: 13.085},
    "B 23 Aravali": {234: 23.725, 191: 6.449},
    192: {191: 29.444, 31: 13.573, 247: 35.528},
    193: {129: 32.869, 194: 32.0},
    194: {193: 32.0, 195: 6.4},
    195: {194: 6.4, 196: 44.816},
    196: {195: 44.816, 197: 33.602000000000004, "Lake Side Gate no. 1": 59.714},
    "Lake Side Gate no. 1": {196: 59.714},
    197: {196: 33.602000000000004, 198: 12.674},
    198: {197: 12.674, 199: 5.913},
    199: {198: 5.913, 200: 220.228},
    200: {199: 220.228, "Padmavati Devi Temple": 208.834},
    "Padmavati Devi Temple": {200: 208.834},
    201: {"QIP 1": 2.536, 202: 9.146, 225: 11.441, 204: 49.64, 203: 31.37, 186: 0.0},
    "QIP 1": {201: 2.536},
    202: {215: 3.25, 203: 6.724, 204: 16.354, "Type1 - 6": 1.985, 201: 9.146},
    "Type1 - 6": {202: 1.985},
    203: {
        "Type1 - 7": 1.2770000000000001,
        204: 2.106,
        239: 14.321,
        202: 6.724,
        201: 31.37,
    },
    "Type1 - 7": {204: 3.005, 203: 1.2770000000000001},
    204: {
        "Type1 - 7": 3.005,
        201: 49.64,
        203: 2.106,
        202: 16.354,
        220: 11.765,
        205: 3.133,
    },
    205: {240: 3.321, 206: 2.997, 204: 3.133},
    206: {224: 1.0, 223: 7.957, 207: 3.9250000000000003, 205: 2.997},
    207: {208: 2.314, 241: 3.321, 206: 3.9250000000000003},
    208: {
        208: 0.0,
        243: 1.352,
        209: 5.7700000000000005,
        "Type 2B 23": 5.7940000000000005,
    },
    "Type 2B 23": {208: 5.7940000000000005},
    209: {208: 5.7700000000000005, 235: 17.849, 210: 5.365, "CSRE C": 1.721},
    "CSRE C": {209: 1.721},
    210: {209: 5.365, 211: 13.537},
    211: {210: 13.537, 212: 5.069, 238: 8.425, 92: 1.549, "Bungalow A16 ": 0.81},
    "Bungalow A16 ": {211: 0.81},
    212: {213: 4.573, "Bungalow A15 ": 1.066, 211: 5.069, 92: 1.018},
    "Bungalow A15 ": {212: 1.066},
    213: {93: 0.081, 92: 9.857, 94: 2.997, "Bungalow A14 ": 1.076, 212: 4.573},
    "Bungalow A14 ": {213: 1.076},
    214: {94: 3.133, 35: 0.388},
    215: {202: 3.25, 216: 2.521, "Type 2B 22": 1.85},
    "Type 2B 22": {215: 1.85},
    216: {215: 2.521, 217: 2.592, 226: 8.002, "Type1 - 18": 1.717, "Type1 - 16": 2.41},
    "Type1 - 18": {216: 1.717},
    "Type1 - 16": {216: 2.41},
    217: {
        216: 2.592,
        239: 1.306,
        218: 1.972,
        227: 7.1290000000000004,
        "Proposed Type H1 Building": 47.765,
    },
    "Proposed Type H1 Building": {226: 11.273, 217: 47.765},
    218: {217: 1.972, 219: 1.405, "Type1 - 14": 1.125, "Type H1 - 12": 2.309},
    "Type1 - 14": {218: 1.125},
    "Type H1 - 12": {218: 2.309},
    219: {218: 1.405, 220: 5.869, 228: 9.685},
    220: {204: 11.765, 239: 4.05, 219: 5.869, "Type1 - 13": 0.405, 222: 8.002},
    "Type1 - 13": {220: 0.405},
    221: {222: 2.665, "Type H1 - 5": 0.245},
    "Type H1 - 5": {221: 0.245},
    222: {221: 2.665, 223: 0.676, 220: 8.002},
    223: {224: 3.321, 222: 0.676, "Type H1 - 6": 2.466},
    "Type H1 - 6": {223: 2.466},
    224: {223: 3.321, 206: 1.0, "Type H1 - 8": 1.481},
    "Type H1 - 8": {224: 1.481},
    225: {201: 11.441, 226: 1.936, "QIP 2": 1.768, 187: 0.405},
    226: {
        226: 0.0,
        216: 8.002,
        227: 4.941,
        187: 0.757,
        "Proposed Type H1 Building": 11.273,
    },
    227: {226: 4.941, 217: 7.1290000000000004, 228: 3.161},
    228: {219: 9.685, 227: 3.161, 230: 5.365, 229: 11.773, 188: 5.869},
    229: {228: 11.773, "Vidya Niwas": 1.45},
    "Vidya Niwas": {229: 1.45},
    230: {228: 5.365, 231: 2.225, "C22, B wing, Vindya": 3.3160000000000003},
    "C22, B wing, Vindya": {230: 3.3160000000000003},
    231: {
        230: 2.225,
        "C22, A wing, Sahyadri": 2.017,
        "K-Yantra Lab (CSE Dept.)": 6.29,
        232: 3.232,
        188: 0.081,
    },
    "C22, A wing, Sahyadri": {231: 2.017},
    232: {244: 2.754, 231: 3.232, 189: 17.849},
    233: {244: 9.928, 234: 7.1290000000000004},
    234: {"B 23 Aravali": 23.725, 233: 7.1290000000000004, 235: 7.688},
    235: {234: 7.688, 209: 17.849},
    236: {237: 4.573, "Bungalow A19 ": 0.9410000000000001, "CSRE D": 1.168},
    "Bungalow A19 ": {236: 0.9410000000000001},
    "CSRE D": {236: 1.168},
    237: {
        236: 4.573,
        238: 3.592,
        "Bungalow A18 ": 0.64,
        "CSRE A": 3.0340000000000003,
        "CSRE B": 0.6980000000000001,
    },
    "Bungalow A18 ": {237: 0.64},
    "CSRE A": {237: 3.0340000000000003},
    "CSRE B": {237: 0.6980000000000001},
    238: {237: 3.592, 211: 8.425, "Bungalow A17 ": 0.65},
    "Bungalow A17 ": {238: 0.65},
    239: {203: 14.321, 220: 4.05, 217: 1.306},
    240: {"Type H2 - 18": 0.901, 205: 3.321},
    "Type H2 - 18": {240: 0.901},
    241: {242: 0.405, "Type H2 - 19": 0.4, 207: 3.321},
    "Type H2 - 19": {241: 0.4},
    242: {241: 0.405, "Type H2 - 20": 2.25},
    "Type H2 - 20": {242: 2.25},
    243: {"Type H2 - 21": 0.925, 208: 1.352},
    "Type H2 - 21": {243: 0.925},
    244: {233: 9.928, 232: 2.754, "Tulsi C": 2.557},
    "Tulsi C": {244: 2.557},
    245: {246: 19.37, "Security Check Point": 15.101, 255: 23.06},
    246: {245: 19.37, "Paspoli Gate no. 4 ": 85.45700000000001},
    "Paspoli Gate no. 4 ": {246: 85.45700000000001},
    247: {192: 35.528, 248: 18.245},
    248: {247: 18.245, "MW Quarters 1": 3.38},
    "MW Quarters 1": {248: 3.38},
    249: {184: 32.405, 250: 29.444, 251: 5.14, "Kendriya Vidyalay Quarters 1": 3.121},
    "Kendriya Vidyalay Quarters 1": {249: 3.121, 251: 6.109},
    250: {
        249: 29.444,
        "Campus School": 22.516000000000002,
        "Kindergarten School": 22.516000000000002,
    },
    "Kindergarten School": {250: 22.516000000000002, 253: 18.769000000000002},
    "Campus School": {250: 22.516000000000002, 253: 18.769000000000002},
    251: {249: 5.14, "Kendriya Vidyalay Quarters 1": 6.109, 252: 23.080000000000002},
    252: {251: 23.080000000000002, 253: 9.217},
    253: {
        252: 9.217,
        254: 12.178,
        160: 160.865,
        "Campus School": 18.769000000000002,
        "Type C-7": 0.116,
        "Kindergarten School": 18.769000000000002,
    },
    "Type C-7": {253: 0.116},
    254: {253: 12.178, "Shivalik C 23 (187-240)": 59.044000000000004},
    "Shivalik C 23 (187-240)": {254: 59.044000000000004},
    255: {2: 325.184, "Security Check Point": 2.125, 245: 23.06},
    "Aromas Canteen": {
        27: 2.669,
        28: 8.845,
        "Hostel 01 Queen of the campus": 13.973,
        "Domino's outlet": 2.041,
    },
}


    '''Caution: Avoid executing the update function during active requests as it may cause significant delays (~20s).
    If any modifications need to be made to the adj_list, it is essential to ensure that the
    adj_list is updated accordingly,
    including the distances between nodes. '''

    def update(self):
        for x in self.adj_list:
            if type(x) != str:
                for y in self.adj_list[x]:
                    if type(y) != str:
                        self.adj_list[x][y] = abs(0.001 * ((self.coordinates[x][0] - self.coordinates[y][0])**2
                                                           + (self.coordinates[x][1] - self.coordinates[y][1])**2))
                    else:
                        try:
                            x_cor = Location.objects.filter(name=y)[0].pixel_x
                            y_cor = Location.objects.filter(name=y)[0].pixel_y
                            if x_cor is None or y_cor is None:
                                x_cor = 0
                                y_cor = 0
                        except IndexError:
                            x_cor = 0
                            y_cor = 0

                        self.adj_list[x][y] = abs(0.001 * ((self.coordinates[x][0] - x_cor)**2
                                                  + (self.coordinates[x][1] - y_cor)**2))

            else:
                try:
                    loc = Location.objects.filter(name=x)[0]
                    x_cor = loc.pixel_x
                    y_cor = loc.pixel_y
                    if x_cor is None or y_cor is None:
                        x_cor = 0
                        y_cor = 0

                except IndexError:
                    x_cor = 0
                    y_cor = 0

                for y in self.adj_list[x]:
                    if type(y) != str:
                        self.adj_list[x][y] = abs(0.001 * ((x_cor - (self.coordinates[y][0]))**2
                                                           + (y_cor - (self.coordinates[y][1]))**2))
                    else:
                        try:
                            x_pix = Location.objects.filter(name=y)[0].pixel_x
                            y_pix = Location.objects.filter(name=y)[0].pixel_y

                        except IndexError:
                            x_pix = 0
                            y_pix = 0
                        if x_pix is None or y_pix is None:
                            x_pix = 0
                            y_pix = 0

                        self.adj_list[x][y] = abs(0.001 * ((x_cor - x_pix)**2 + (y_cor - y_pix)**2))
            # Need to run this once to update the database with given new or updated node points.
            i = 0
            loc_list = []
            for p in self.coordinates:
                loc, c = Location.objects.get_or_create(pixel_x=p[0], pixel_y=p[1], name="Node" + str(i))
                loc_list.append(loc)
                i += 1

    '''Gets the nearest Node near a location on the map.'''

    import sys

    def get_nearest(self, loc):
        if "Node" in loc:
            k = int(loc.replace("Node", ""))
            return k

        min_dist = sys.maxsize
        nearest_loc = None

        try:
            sets = self.adj_list[loc]
            for i in sets:
                if isinstance(i, int):
                    if sets[i] <= min_dist:
                        min_dist = sets[i]
                        nearest_loc = i
        except KeyError:
            print(f"This Location: {loc} does not exist in adj_list")

        return nearest_loc


    '''Returns the adj_list which contains only the node points containing the endpoint and the start point'''

    def graph(self, end, start):
        new_adjoint_list = {}
        for i in self.adj_list:
            if isinstance(i, int) or i == start or i == end:
                new_adjoint_list[i] = {}
                for j in self.adj_list[i]:
                    if isinstance(j, int) or j == start or j == end:
                        new_adjoint_list[i][j] = self.adj_list[i][j]

        return new_adjoint_list


def dijkstra(graph, start, goal):
    shortest_dist = {}
    track_pred = {}
    unseenNodes = graph
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
            print(f"Path is not reachable start : {start}, end: {goal}")

            return None
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


''' This command gets the nearest points for some x,y coordinates. Although a simliar function is defined in views.py'''
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
            filtered_locations = Location.objects.filter(
                Q(name__contains="Node"),
                pixel_x__range=[xcor - 1200, xcor + 1200],
                pixel_y__range=[ycor - 1200, ycor + 1200])
            # filtered_locations = location.filter
            # (pixel_x__range=[xcor - 400, xcor +   # 400], pixel_y__range=[ycor - 400, ycor # + 400])
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
