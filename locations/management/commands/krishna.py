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
def handle_entry():
    coordinates = [(2269, 3204), (2394, 2910), (2394, 3106), (2786, 2510), (2732, 2447), (3026, 2252), (3266, 2332), (3462, 2394), (3649, 2447), (4014, 2590), (3907, 2768), (4076, 2812), (3792, 2919), (3640, 2857), (3409, 2768), (3462, 2946), (3124, 3017), (2973, 2990), (3062, 2848), (2830, 2928), (2964, 2599), (2581, 3177), (2706, 2857), (2830, 2554), (2296, 774), (2492, 845), (2795, 1094), (2866, 1166), (3142, 1397), (3898, 1246), (4005, 1192), (4335, 996), (3845, 1130), (3792, 1166), (3204, 952), (2608, 1272), (2732, 1584), (2545, 1673), (2528, 1726), (2581, 1753), (2688, 1726), (2866, 1833), (2447, 2216), (2376, 2403), (2261, 2483), (1735, 2759), (1531, 2804), (1771, 2910), (1869, 3035),(2189, 2946), (2376, 2581), (2608, 2385), (2581, 2278), (2741, 2154), (2901, 2216), (3071, 2056), (3302, 1833), (1192, 2634), (1041, 2625), (738, 2474), (721, 2376), (640, 2376), (4619, 1646), (4522, 1620), (4406, 1575), (4344, 1548), (4237, 1522), (4148, 1504), (3943, 1442), (3685, 1361), (3338, 1531), (3418, 1664), (3453, 1700), (3373, 1851), (3391, 1913), (3551, 1976), (3783, 1726), (4059, 1798), (4281, 1860), (4335, 1807), (4486, 1842), (4174, 2047), (4352, 2118), (4121, 2474), (4468, 2136), (4530, 1993), (4557, 1878), (4433, 1468), (4032, 1584), (4183, 1646), (3863, 1620), (3747, 1771), (3649, 1869), (3498, 2047), (3436, 2118), (3338, 2243), (3729, 2198), (4228, 1940), (3970, 2474), (3614, 1824), (3890, 1201), (2821, 1050), (2643, 1059)]
    adj_list = {
        0: {
            2: -1,
            "Main Gate no. 2": -1,
            "State Bank of India, IIT Powai branch": -1,
            "Bungalow A8 ": -1,
            "Bungalow A7 ": -1,
            "Bungalow A6 ": -1,
        },
        "Main Gate no. 2": {0: -1},
        "State Bank of India, IIT Powai branch": {0: -1},
        "Bungalow A8 ": {0: -1, 1: -1, 49: -1},
        "Bungalow A7 ": {0: -1, 1: -1, 49: -1},
        "Bungalow A6 ": {0: -1, 1: -1, 49: -1},
        1: {
            2: -1,
            3: -1,
            22: -1,
            "Shishu Vihar": -1,
            "Bungalow A8 ": -1,
            "Bungalow A7 ": -1,
            "Bungalow A6 ": -1,
            "Bungalow A4 ": -1,
            "Bungalow A3 ": -1,
            "Bungalow A2 ": -1,
            "A1 Director Bungalow": -1,
            49: -1,
        },
        "Shishu Vihar": {1: -1, 49: -1},
        "Bungalow A4 ": {1: -1, 4: -1, 50: -1},
        "Bungalow A3 ": {1: -1, 4: -1, 50: -1},
        "Bungalow A2 ": {1: -1, 4: -1, 50: -1},
        "A1 Director Bungalow": {1: -1, 4: -1, 51: -1},
        2: {
            0: -1,
            22: -1,
            21: -1,
            1: -1,
            "Type B-8": -1,
            "Type B-7": -1,
            "Type B-9": -1,
            "Type B-10": -1,
        },
        "Type B-8": {2: -1, 3: -1, 22: -1},
        "Type B-7": {2: -1, 3: -1, 21: -1, 22: -1},
        "Type B-9": {2: -1, 3: -1, 22: -1, 23: -1},
        "Type B-10": {2: -1, 3: -1, 22: -1, 23: -1},
        3: {
            1: -1,
            4: -1,
            5: -1,
            23: -1,
            "Hostel 10 Annexe (Girls Hostel)": -1,
            "Hostel 10 Phoenix (Girls Hostel)": -1,
            "Type B-8": -1,
            "Type B-7": -1,
            "Type B-9": -1,
            "Type B-10": -1,
        },
        "Hostel 10 Annexe (Girls Hostel)": {3: -1, 5: -1},
        "Hostel 10 Phoenix (Girls Hostel)": {3: -1, 5: -1},
        4: {
            3: -1,
            5: -1,
            "Bungalow A4 ": -1,
            "Bungalow A3 ": -1,
            "Bungalow A2 ": -1,
            "A1 Director Bungalow": -1,
            "Type B-1": -1,
            51: -1,
        },
        "Type B-1": {4: -1, 51: -1},
        5: {4: -1, 6: -1, "Gulmohar Restaurant": -1, "Hostel 10 Annexe (Girls Hostel)": -1, "Hostel 10 Phoenix (Girls Hostel)": -1, 54: -1, 55: -1},
        "Gulmohar Restaurant": {5: -1, 54: -1},
        6: {
            5: -1,
            7: -1,
            20: -1,
            "B 24 Nilgiri": -1,
            "Type B-18": -1,
            "Type B-17": -1,
            "Type C-2": -1,
        },
        "B 24 Nilgiri": {6: -1},
        "Type B-18": {6: -1, 20: -1},
        "Type B-17": {6: -1, 20: -1},
        "Type C-2": {6: -1, 20: -1},
        7: {6: -1, 8: -1, 14: -1, "Type C-5": -1, "B 21 Satpura": -1, 95: -1, 96: -1},
        "Type C-5": {7: -1, 14: -1},
        "B 21 Satpura": {7: -1, 14: -1},
        8: {7: -1, 9: -1, 96: -1},
        9: {
            8: -1,
            10: -1,
            83: -1,
            "Kendriya Vidyalaya ": -1,
            "DESE & CESE New Building": -1,
            "Type1 - 1": -1,
            "Type1 - 2": -1,
            "Type1 - 3": -1,
            "Type1 - 4": -1,
            "Cafe Coffee Day": -1
        },
        "Kendriya Vidyalaya ": {9: -1, 10: -1},
        "DESE & CESE New Building": {9: -1},
        "Type1 - 1": {9: -1},
        "Type1 - 2": {9: -1},
        "Type1 - 3": {9: -1},
        "Type1 - 4": {9: -1},
        10: {9: -1, 11: -1, 12: -1, "Kendriya Vidyalaya ": -1, "Medical Store": -1, "Post Office": -1},
        "Medical Store": {10: -1},
        "Post Office": {10: -1, 12: -1},
        11: {10: -1, "Uphar": -1},
        "Uphar": {11: -1},
        12: {10: -1, 13: -1, "Market Gate, Y point Gate no. 3": -1, "Post Office": -1},
        "Market Gate, Y point Gate no. 3": {12: -1},
        13: {
            12: -1,
            14: -1,
            15: -1,
            "Kendriya Vidyalay Quarters 1": -1,
            "Kendriya Vidyalay Quarters 2": -1,
            "Type C-6": -1,
        },
        "Kendriya Vidyalay Quarters 1": {13: -1},
        "Kendriya Vidyalay Quarters 2": {13: -1},
        "Type C-6": {13: -1, 14: -1},
        14: {
            7: -1,
            13: -1,
            "Type C-5": -1,
            "B 21 Satpura": -1,
            "Type C-7": -1,
            "Type C-6": -1,
            "Shivalik C 23 (187-240)": -1,
        },
        "Type C-7": {14: -1},
        "Shivalik C 23 (187-240)": {14: -1},
        15: {
            13: -1,
            16: -1,
            "Type C-18": -1,
            "Campus School": -1,
            "Type C-17": -1,
            "Type C-15": -1,
        },
        "Type C-18": {15: -1},
        "Campus School": {15: -1, 16: -1},
        "Type C-17": {15: -1, 16: -1},
        "Type C-15": {15: -1, 16: -1},
        16: {
            15: -1,
            17: -1,
            18: -1,
            "Campus School": -1,
            "Type C-17": -1,
            "Type C-15": -1,
            "Type C-16": -1,
            "Type C-14": -1,
            "Type C-13": -1,
        },
        "Type C-16": {16: -1},
        "Type C-14": {16: -1},
        "Type C-13": {16: -1, 17: -1},
        17: {16: -1, 19: -1, "Type C-13": -1},
        18: {16: -1, 19: -1, "Type C-8": -1},
        "Type C-8": {18: -1},
        19: {
            17: -1,
            18: -1,
            20: -1,
            21: -1,
            22: -1,
            "Type C-9": -1,
            "Type C-12": -1,
            "Type C-11": -1,
            "Type C-10": -1,
        },
        "Type C-9": {19: -1},
        "Type C-12": {19: -1, 21: -1},
        "Type C-11": {19: -1, 21: -1},
        "Type C-10": {19: -1, 20: -1, 22: -1},
        20: {
            23: -1,
            6: -1,
            22: -1,
            19: -1,
            18: -1,
            "Type C-10": -1,
            "Type C-2": -1,
            "Type B-17": -1,
            "Type B-18": -1,
        },
        21: {
            2: -1,
            22: -1,
            19: -1,
            17: -1,
            "Type B-5": -1,
            "Type B-6": -1,
            "Type C-11": -1,
            "Type B-7": -1,
            "Type B-4": -1,
            "Type C-12": -1,
        },
        "Type B-5": {21: -1, 22: -1},
        "Type B-6": {21: -1},
        "Type B-4": {21: -1, 22: -1},
        22: {
            1: -1,
            2: -1,
            19: -1,
            21: -1,
            23: -1,
            20: -1,
            18: -1,
            "Type B-8": -1,
            "Type B-2": -1,
            "Type B-7": -1,
            "Type B-9": -1,
            "Type B-10": -1,
            "Type B-3": -1,
            "Type B-4": -1,
            "Type B-5": -1,
            "Type C-10": -1,
        },
        "Type B-2": {22: -1, 23: -1},
        "Type B-3": {22: -1, 23: -1},
        23: {
            3: -1,
            20: -1,
            22: -1,
            "Type B-9": -1,
            "Type B-2": -1,
            "Type B-10": -1,
            "Type B-3": -1,
        },
        24: {
            "Mess for hostels 12 | 13 | 14": -1,
            "Hostel 12 Crown of the Campus": -1,
            "Hostel 13 House of Titans": -1,
            "Hostel 14 Silicon Ship": -1,
            25: -1,
            "Security Check Point": -1,
        },
        "Mess for hostels 12 | 13 | 14": {24: -1},
        "Hostel 12 Crown of the Campus": {24: -1},
        "Hostel 13 House of Titans": {24: -1},
        "Hostel 14 Silicon Ship": {24: -1},
        "Security Check Point": {24: -1},
        25: {
            "Hostel 06 Vikings": -1,
            "Hostel 07 Lady of the Lake": -1,
            "Hostel 09 Nawaabon Ki Basti": -1,
            "ATM - Canara Bank near H6": -1,
            24: -1,
            26: -1,
            "Type1 - 22": -1,
            "Hostel 18": -1,
            "Hostel 17": -1
        },
        "Hostel 06 Vikings": {25: -1},
        "Hostel 07 Lady of the Lake": {25: -1},
        "Hostel 09 Nawaabon Ki Basti": {25: -1},
        "ATM - Canara Bank near H6": {25: -1},
        "Type1 - 22": {25: -1},
        "Hostel 18": {25: -1, 26: -1},
        26: {"Hostel 05 Penthouse": -1, 27: -1, 34: -1, "Hostel 18": -1, "Chaayos Cafe": -1, "Hostel 17": -1},
        "Hostel 05 Penthouse": {26: -1},
        27: {
            26: -1,
            28: -1,
            35: -1,

            "Gymkhana Grounds": -1,
            "Gymkhana Building": -1,
            "Basketball Court": -1,
            "Hostel 11 Athena (Girls Hostel)": -1,
            "Brewberrys Cafe": -1,
        },
        "Gymkhana Grounds": {27: -1, 28: -1},
        "Gymkhana Building": {27: -1, 28: -1},
        "Basketball Court": {27: -1, 28: -1},
        "Hostel 11 Athena (Girls Hostel)": {27: -1, 28: -1},
        "Brewberrys Cafe": {27: -1, 28: -1},
        28: {
            27: -1,
            70: -1,
            "Gymkhana Grounds": -1,
            "Gymkhana Building": -1,
            "Basketball Court": -1,
            "Hostel 11 Athena (Girls Hostel)": -1,
            "Brewberrys Cafe": -1,
            "Staff Hostel": -1,
            "Tennis Court (new)": -1,
            "Squash Court": -1,
            "Tennis Court (old)": -1,
            "Hockey Ground": -1,
        },
        "Staff Hostel": {28: -1},
        "Tennis Court (new)": {28: -1},
        "Squash Court": {28: -1},
        "Tennis Court (old)": {28: -1},
        "Hockey Ground": {28: -1},
        29: {30: -1, "State Bank of India Branch": -1, "Bungalow A14 ": -1, "Bungalow A15 ": -1, 69: -1, "Dominoes outlet": -1},
        "State Bank of India Branch": {29: -1},
        "Bungalow A14 ": {29: -1},
        "Bungalow A15 ": {29: -1},
        30: {
            29: -1,
            31: -1,
            32: -1,
            "Bungalow A16 ": -1,
            "Bungalow A17 ": -1,
            "Bungalow A18 ": -1,
            "Bungalow A19 ": -1,
            "Defence Research & Development Organization": -1,
        },
        "Bungalow A16 ": {30: -1},
        "Bungalow A17 ": {30: -1},
        "Bungalow A18 ": {30: -1},
        "Bungalow A19 ": {30: -1},
        "Defence Research & Development Organization": {30: -1},
        31: {30: -1, "Hostel 15 Trident": -1, "Hostel 16 Olympus": -1, "B 23 Aravali": -1, "Society for Applied Microwave Electronics Engineering & Research": -1},
        "Hostel 15 Trident": {31: -1},
        "Hostel 16 Olympus": {31: -1},
        "B 23 Aravali": {31: -1},
        "Society for Applied Microwave Electronics Engineering & Research": {31: -1},
        32: {30: -1, 33: -1, "Hostel 01 Queen of the campus": -1},
        "Hostel 01 Queen of the campus": {32: -1},
        33: {32: -1, 34: -1, "Indoor Stadium": -1, "Students Activity Centre": -1, "Hostel 02 The Wild Ones": -1, "Swimming Pool (new)": -1},
        "Indoor Stadium": {33: -1},
        "Students Activity Centre": {33: -1},
        "Hostel 02 The Wild Ones": {33: -1},
        "Swimming Pool (new)": {33: -1},
        34: {
            33: -1,
            "Outdoor Sports Facility": -1,
            "Hostel 04 MadHouse": -1,
            "Tansa House King of campus (Proj. Staff Boys)": -1,
            26: -1,
            "Hostel 03 Vitruvians": -1,
            "Type1 - 11": -1,
        },
        "Outdoor Sports Facility": {34: -1},
        "Hostel 04 MadHouse": {34: -1},
        "Tansa House King of campus (Proj. Staff Boys)": {34: -1},
        "Hostel 03 Vitruvians": {34: -1},
        "Type1 - 11": {34: -1},
        35: {36: -1, 27: -1},
        36: {35: -1, 37: -1},
        37: {36: -1, 38: -1},
        38: {"Boat House": -1, 37: -1, 39: -1},
        "Boat House": {38: -1},
        39: {38: -1, 40: -1},
        40: {39: -1, 41: -1},
        41: {
            40: -1,
            42: -1,
            "National Centre for Mathematics": -1,
            "Kshitij Udyan": -1,
            "Guest House / Padmavihar": -1,
            "Guest House / Jalvihar": -1,
        },
        "National Centre for Mathematics": {41: -1},
        "Kshitij Udyan": {41: -1},
        "Guest House / Padmavihar": {41: -1},
        "Guest House / Jalvihar": {41: -1, 42: -1},
        42: {41: -1, 43: -1, 52: -1, "Guest House / Jalvihar": -1, "Type B-14": -1},
        "Type B-14": {42: -1},
        43: {42: -1, 44: -1},
        44: {
            43: -1,
            45: -1,
            50: -1,
            "Type B-13": -1,
            "Type B-11": -1,
            "Type B-12": -1,
            "Type B-15": -1,
            "Type B-16": -1,
        },
        "Type B-13": {44: -1},
        "Type B-11": {44: -1},
        "Type B-12": {44: -1},
        "Type B-15": {44: -1},
        "Type B-16": {44: -1},
        45: {44: -1, 46: -1},
        46: {45: -1, 47: -1, 57: -1, "B 19 Old Multistoried Building- Residence ": -1},
        "B 19 Old Multistoried Building- Residence ": {46: -1},
        47: {46: -1, 48: -1, "White House": -1, "CTR 20": -1},
        "White House": {47: -1},
        "CTR 20": {47: -1},
        48: {
            47: -1,
            49: -1,
            "CTR 19": -1,
            "Bungalow A9 ": -1,
            "Bungalow A10 ": -1,
            "BTR Building - A & B": -1,
        },
        "CTR 19": {48: -1},
        "Bungalow A9 ": {48: -1},
        "Bungalow A10 ": {48: -1},
        "BTR Building - A & B": {48: -1},
        49: {
            48: -1,
            50: -1,
            1: -1,
            "Bungalow A11 ": -1,
            "Bungalow A12 ": -1,
            "Bungalow A6 ": -1,
            "Bungalow A7 ": -1,
            "Bungalow A8 ": -1,
            "Shishu Vihar": -1,
        },
        "Bungalow A11 ": {49: -1},
        "Bungalow A12 ": {49: -1},
        50: {49: -1, 51: -1, "Bungalow A2 ": -1, "Bungalow A3 ": -1, "Bungalow A4 ": -1},
        51: {
            50: -1,
            52: -1,
            "A1 Director Bungalow": -1,
            "Bungalow A13 ": -1,
            "Type B-1": -1,
            4: -1,
        },
        "Bungalow A13 ": {51: -1},
        52: {42: -1, 51: -1, 53: -1},
        53: {52: -1, 54: -1},
        54: {53: -1, 55: -1, "Gulmohar Restaurant": -1, "Guest House / Vanvihar": -1, 5: -1},
        "Guest House / Vanvihar": {54: -1},
        55: {54: -1, 56: -1, 74: -1, "Hospital": -1, "Staff Club": -1, 5: -1},
        "Hospital": {55: -1},
        "Staff Club": {55: -1},
        56: {55: -1, 73: -1, "Convocation Hall": -1, "Type1 - 15": -1, "Type H2 - 17": -1},
        "Convocation Hall": {56: -1, 71: -1, 72: -1},
        "Type1 - 15": {56: -1},
        "Type H2 - 17": {56: -1},
        57: {46: -1, 58: -1},
        58: {57: -1, 59: -1, "Lake Side Gate no. 1": -1},
        "Lake Side Gate no. 1": {58: -1},
        59: {58: -1, 60: -1},
        60: {59: -1, 61: -1},
        61: {60: -1, "Padmavati Devi Temple": -1},
        "Padmavati Devi Temple": {61: -1},
        62: {63: -1, "OrthoCad Lab": -1, "Power House": -1, "Hostel 10A QIP (Girls Hostel)": -1},
        "OrthoCad Lab": {62: -1, 80: -1},
        "Power House": {62: -1},
        "Hostel 10A QIP (Girls Hostel)": {62: -1},
        63: {64: -1, 62: -1, "Physics Lab (Ist Years)": -1},
        "Physics Lab (Ist Years)": {63: -1},
        64: {
            65: -1,
            63: -1,
            "SMAmL Suman Mashruwala Advanced Microengineering Lab": -1,
            "Thermal Hydraulic Test Facility": -1,
        },
        "SMAmL Suman Mashruwala Advanced Microengineering Lab": {64: -1},
        "Thermal Hydraulic Test Facility": {64: -1},
        65: {
            66: -1,
            87: -1,
            64: -1,
            "Heat Transfer and Thermodynamic Lab": -1,
            "Cummins Engine Research facility": -1,
        },
        "Heat Transfer and Thermodynamic Lab": {65: -1},
        "Cummins Engine Research facility": {65: -1},
        66: {
            67: -1,
            65: -1,
            "Heat Pump Lab": -1,
            "Geotechnical Engg. Lab": -1,
            "National Geotechnical Centrifuge Facility": -1,
        },
        "Heat Pump Lab": {66: -1},
        "Geotechnical Engg. Lab": {66: -1},
        "National Geotechnical Centrifuge Facility": {66: -1},
        67: {68: -1, 88: -1, 66: -1, "Fluid Mechanics and Fluid Power Lab": -1},
        "Fluid Mechanics and Fluid Power Lab": {67: -1, 88: -1},
        68: {
            69: -1,
            67: -1,
            "Mathematics Department": -1,
            "Central Library": -1,
            90: -1,
            "Inter-disciplinary Programme in Systems and Control Engineering": -1,
            "NanoTech. & Science Research Centre": -1,
        },
        "Mathematics Department": {68: -1},
        "Central Library": {68: -1},
        "Inter-disciplinary Programme in Systems and Control Engineering": {68: -1},
        "NanoTech. & Science Research Centre": {68: -1},
        69: {70: -1, 68: -1, 29: -1},
        70: {71: -1, 69: -1, 28: -1, "NCC Office": -1},
        "NCC Office": {70: -1},
        71: {72: -1, 70: -1, "Convocation Hall": -1},
        72: {
            73: -1,
            71: -1,
            "Convocation Hall": -1,
            "Main Building": -1,
            "Staff Canteen": -1,
        },
        "Main Building": {72: -1, 76: -1},
        "Staff Canteen": {72: -1},
        73: {74: -1, 72: -1, 56: -1},
        74: {75: -1, 73: -1, 55: -1, "School of Management": -1, "Computer Centre": -1},
        "School of Management": {74: -1},
        "Computer Centre": {74: -1, 93: -1},
        75: {92: -1, 93: -1, "Girish Gaitonde Building": -1, "Seminar Hall": -1},
        "Girish Gaitonde Building": {75: -1},
        "Seminar Hall": {75: -1},
        76: {91: -1, 90: -1, 77: -1, "Main Building": -1},
        77: {89: -1, 78: -1, 76: -1, "Electrical Engineering Annexe Building": -1},
        "Electrical Engineering Annexe Building": {77: -1},
        78: {
            79: -1,
            77: -1,
            97: -1,
            "Non- Academic Staff Association": -1,
            "Victor Menezes Convention Centre": -1,
            "Industrial Design Centre": -1,
        },
        "Non- Academic Staff Association": {78: -1},
        "Victor Menezes Convention Centre": {78: -1, 97: -1},
        "Industrial Design Centre": {78: -1, 89: -1},
        79: {80: -1, 78: -1, "Structural integrity Testing and Analysis Centre": -1},
        "Structural integrity Testing and Analysis Centre": {79: -1},
        80: {
            86: -1,
            79: -1,
            62: -1,
            "Electrical Maintenence": -1,
            "Micro Fluidics Lab": -1,
            "OrthoCad Lab": -1,
        },
        "Electrical Maintenence": {80: -1},
        "Micro Fluidics Lab": {80: -1},
        81: {
            97: -1,
            82: -1,
            "Centre of Studies in Resources Engineering": -1,
            "Energy Science and Engineering": -1,
            "Earth Science Department": -1,
            "Rock Powdering Lab": -1,
        },
        "Centre of Studies in Resources Engineering": {81: -1},
        "Energy Science and Engineering": {81: -1},
        "Earth Science Department": {81: -1},
        "Rock Powdering Lab": {81: -1},
        82: {
            83: -1,
            84: -1,
            81: -1,
            "ONGC Research Centre": -1,
            "Proposed Building for Tata Centre for Technology": -1,
            "Aerospace Engineering Department": -1,
        },
        "ONGC Research Centre": {82: -1},
        "Proposed Building for Tata Centre for Technology": {82: -1, 84: -1},
        "Aerospace Engineering Department": {82: -1, 83: -1},
        83: {
            82: -1,
            9: -1,
            "Aerospace Engineering Department": -1,
            "Chemical Engineering Department": -1,
        },
        "Chemical Engineering Department": {83: -1},
        84: {85: -1, 82: -1, "Proposed Building for Tata Centre for Technology": -1},
        85: {86: -1, 84: -1},
        86: {80: -1, 85: -1, "Electrical Maintenence": -1},
        "Electrical Maintenence": {86: -1},
        87: {65: -1, "GMFL Lab / Geophysical and multiphase Flows Lab": -1},
        "GMFL Lab / Geophysical and multiphase Flows Lab": {87: -1},
        88: {
            89: -1,
            67: -1,
            "Old Computer Science Engineering Department": -1,
            "Fluid Mechanics and Fluid Power Lab": -1,
        },
        "Old Computer Science Engineering Department": {88: -1},
        89: {88: -1, "Treelabs": -1, "Industrial Design Centre": -1},
        "Treelabs": {89: -1},
        90: {68: -1, 76: -1, "Mechanical Engineering Department": -1},
        "Mechanical Engineering Department": {90: -1},
        91: {76: -1, 92: -1, "Civil Engineering Department": -1, "LTPCSA": -1},
        "Civil Engineering Department": {91: -1},
        "LTPCSA": {91: -1},
        92: {91: -1, 75: -1, "Electrical Engineering Department": -1, "Cafe 92": -1},
        "Electrical Engineering Department": {92: -1},
        93: {
            75: -1,
            94: -1,
            "Computer Centre": -1,
            "Metallurgical Engineering and Material Science Department": -1,
        },
        "Metallurgical Engineering and Material Science Department": {93: -1},
        94: {93: -1, 95: -1, "Lecture Hall Complex - 1 & 2": -1, "Kanwal Rekhi School of Information Technology": -1},
        "Lecture Hall Complex - 1 & 2": {94: -1, 96: -1},
        "Kanwal Rekhi School of Information Technology": {94: -1},
        95: {94: -1, "Physics Department": -1, 7: -1},
        "Physics Department": {95: -1},
        96: {
            77: -1,
            7: -1,
            8: -1,
            "Lecture Hall Complex - 3": -1,
            "Lecture Hall Complex - 1 & 2": -1,
            "Humanities and Social Sciences Department": -1,
            "Biosciences and Bioengineering Department": -1,
        },
        "Lecture Hall Complex - 3": {96: -1},
        "Humanities and Social Sciences Department": {96: -1},
        "Biosciences and Bioengineering Department": {96: -1},
        97: {
            78: -1,
            81: -1,
            "Victor Menezes Convention Centre": -1,
            "Centre for Environmental Science and Engineering": -1,
        },
        "Centre for Environmental Science and Engineering": {97: -1},
        "Cafe Coffee Day": {9: -1},
        "Cafe 92": {92: -1},
        "Dominoes outlet": {29: -1},
        "Chaayos Cafe": {26: -1},
        "Hostel 17": {25: -1, 26: -1}
    }

    
    for x in adj_list:
        if type(x) != str:
            for y in adj_list[x]:
                if type(y) != str:
                    adj_list[x][y] = abs(0.001 * ((coordinates[x][0]  - (coordinates[y][0]) )**2 +
                                    (coordinates[x][1] - (coordinates[y][1] ))**2))
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

                    adj_list[x][y] = abs(0.001 * ((coordinates[x][0]  - x_cor) )**2 +
                                        (coordinates[x][1] - y_cor)**2)
                    
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
        
            for y in adj_list[x]:
                if type(y) != str:
                    adj_list[x][y] = abs(0.001 * ((x_cor  - (coordinates[y][0]) )**2 +
                                    (y_cor - (coordinates[y][1] ))**2))
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
                    
                    adj_list[x][y] = abs(0.001 * ((x_cor  - x_pix) )**2 +
                                        (y_cor - y_pix)**2)


    # Need to run this once to update the database with given new or updated node points.
    i = 0
    loc_list = []
    for p in coordinates:
        loc, c = Location.objects.get_or_create(pixel_x=p[0], pixel_y=p[1], name="Node" + str(i))
        loc_list.append(loc)
        i += 1
    
    return adj_list


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
            print("Path is not reachable")
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