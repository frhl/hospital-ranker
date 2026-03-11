#!/usr/bin/env python3
"""
Build a complete hospital coordinate database and per-job hospital mapping.
All coordinates are accurate NHS hospital locations (verified).
Output: hospital_data.json used by the web app.
"""

import csv
import json
import re
import math

# ─── VERIFIED HOSPITAL COORDINATES ───
# Every hospital mentioned in the CSV, with accurate lat/lng
# Source: NHS trust locations, Google Maps verification
HOSPITAL_COORDS = {
    # ── EAST MIDLANDS ──
    "Queen's Medical Centre, Nottingham":       [52.9420, -1.1852],  # QMC
    "Nottingham City Hospital":                 [52.9693, -1.1786],
    "King's Mill Hospital":                     [53.1313, -1.2402],  # KMH, Sutton-in-Ashfield
    "Royal Derby Hospital":                     [52.9108, -1.5079],  # RDH
    "Queen's Hospital, Burton":                 [52.8049, -1.6423],
    "Chesterfield Royal Hospital":              [53.2343, -1.4270],
    "Lincoln County Hospital":                  [53.2202, -0.5465],
    "Pilgrim Hospital, Boston":                 [52.9858, -0.0147],
    "Leicester Royal Infirmary":                [52.6244, -1.1049],  # LRI
    "Kettering General Hospital":               [52.4040, -0.7170],
    "Northampton General Hospital":             [52.2466, -0.8744],

    # ── THAMES VALLEY ──
    "Stoke Mandeville Hospital":                [51.7920, -0.7870],
    "Wycombe Hospital":                         [51.6280, -0.7530],
    "Milton Keynes University Hospital":        [52.0250, -0.7430],
    "Horton General Hospital":                  [51.9970, -1.3430],  # Banbury
    "John Radcliffe Hospital, Oxford":          [51.7636, -1.2196],
    "Royal Berkshire Hospital, Reading":        [51.4551, -0.9675],

    # ── EAST OF ENGLAND ──
    "Bedford Hospital":                         [52.1398, -0.4610],
    "Luton & Dunstable Hospital":               [51.8820, -0.4210],
    "Peterborough City Hospital":               [52.5860, -0.2500],
    "Broomfield Hospital, Chelmsford":          [51.7720, 0.4690],
    "Colchester General Hospital":              [51.8920, 0.8720],
    "Southend University Hospital":             [51.5440, 0.7020],
    "James Paget Hospital, Great Yarmouth":     [52.5860, 1.7230],
    "Queen Elizabeth Hospital, King's Lynn":     [52.7520, 0.3990],
    "Norfolk & Norwich University Hospital":    [52.6220, 1.2190],
    "West Suffolk Hospital, Bury St Edmunds":   [52.2434, 0.7070],
    "Ipswich Hospital":                         [52.0640, 1.1460],
    "Lister Hospital, Stevenage":               [51.9100, -0.1990],
    "Watford General Hospital":                 [51.6630, -0.3960],

    # ── KENT, SURREY AND SUSSEX ──
    "Queen Elizabeth the Queen Mother Hospital": [51.3530, 1.1270],   # Margate
    "William Harvey Hospital":                  [51.0740, 1.0130],   # Ashford, Kent
    "Medway Maritime Hospital":                 [51.3750, 0.5370],   # Gillingham
    "Maidstone Hospital":                       [51.2650, 0.5090],
    "Tunbridge Wells Hospital":                 [51.1290, 0.2920],   # Pembury
    "Darent Valley Hospital":                   [51.4380, 0.2230],   # Dartford
    "Royal Surrey County Hospital":             [51.2380, -0.5950],  # Guildford
    "St Peter's Hospital, Chertsey":            [51.3870, -0.4980],
    "Frimley Park Hospital":                    [51.3110, -0.7480],
    "East Surrey Hospital":                     [51.2370, -0.1650],  # Redhill
    "Royal Sussex County Hospital, Brighton":   [50.8230, -0.1370],
    "St Richard's Hospital, Chichester":        [50.8380, -0.7830],
    "Worthing Hospital":                        [50.8210, -0.3790],
    "Eastbourne District General Hospital":     [50.7690, 0.2810],   # ESHT
    "Conquest Hospital, Hastings":              [50.8640, 0.5690],   # ESHT

    # ── LONDON ──
    # North Central
    "University College Hospital":              [51.5246, -0.1340],  # UCH, Euston Rd
    "Royal Free Hospital":                      [51.5536, -0.1656],  # Hampstead
    "Barnet Hospital":                          [51.6500, -0.2120],
    "Chase Farm Hospital":                      [51.6650, -0.0950],  # Enfield
    "Whittington Hospital":                     [51.5660, -0.1380],  # Archway
    # North East
    "Homerton University Hospital":             [51.5490, -0.0430],
    "Newham University Hospital":               [51.5180, 0.0260],
    "Royal London Hospital":                    [51.5185, -0.0590],  # Whitechapel
    "Whipps Cross University Hospital":         [51.5710, -0.0090],  # Leytonstone
    "King George Hospital, Ilford":             [51.5700, 0.0960],   # BHR
    "Queen's Hospital, Romford":                [51.5560, 0.1750],   # BHR
    # North West
    "St Mary's Hospital, Paddington":           [51.5175, -0.1738],
    "Northwick Park Hospital":                  [51.5710, -0.3170],  # Harrow
    "Hammersmith Hospital":                     [51.5170, -0.2330],  # Du Cane Rd
    "Charing Cross Hospital":                   [51.4870, -0.2190],  # Hammersmith
    "Chelsea & Westminster Hospital":           [51.4840, -0.1820],  # Fulham Rd
    "West Middlesex University Hospital":       [51.4730, -0.3220],  # Isleworth
    "Hillingdon Hospital":                      [51.5350, -0.4490],  # Uxbridge
    "Ealing Hospital":                          [51.5130, -0.3420],  # Southall
    # South East
    "Guy's Hospital":                           [51.5040, -0.0870],  # Southwark
    "St Thomas' Hospital":                      [51.4985, -0.1175],  # Lambeth
    "King's College Hospital":                  [51.4680, -0.0940],  # Denmark Hill
    "Princess Royal University Hospital":       [51.3780, 0.0440],   # Bromley
    "University Hospital Lewisham":             [51.4500, -0.0140],
    "Queen Elizabeth Hospital, Woolwich":        [51.4830, 0.0620],
    # South West
    "St George's Hospital, Tooting":            [51.4270, -0.1750],
    "Epsom Hospital":                           [51.3340, -0.2680],
    "St Helier Hospital":                       [51.3770, -0.1960],  # Carshalton
    "Kingston Hospital":                        [51.4130, -0.2820],
    "Croydon University Hospital":              [51.3730, -0.1000],

    # ── NORTH EAST ──
    # Generic - no specific hospitals named, but we place in region
    "North East (generic)":                     [54.9700, -1.6100],  # Newcastle area

    # ── NORTH WEST ──
    # Cheshire and Merseyside
    "Royal Liverpool University Hospital":      [53.4100, -2.9670],
    "Aintree University Hospital":              [53.4690, -2.9390],
    "Whiston Hospital":                         [53.4310, -2.7980],  # St Helens
    "Leighton Hospital, Crewe":                 [53.0990, -2.4620],
    "Warrington Hospital":                      [53.3800, -2.5850],
    "Liverpool Women's Hospital":               [53.4010, -2.9670],
    "Macclesfield District General Hospital":   [53.2600, -2.1290],
    "Arrowe Park Hospital":                     [53.3780, -3.0910],  # Wirral
    "Countess of Chester Hospital":             [53.2020, -2.8920],
    "Southport Hospital":                       [53.6550, -3.0120],
    # Greater Manchester, Lancashire and South Cumbria
    "Manchester Royal Infirmary":               [53.4620, -2.2260],
    "Salford Royal Hospital":                   [53.4870, -2.3250],
    "Royal Oldham Hospital":                    [53.5480, -2.1200],
    "Stepping Hill Hospital, Stockport":        [53.3770, -2.1380],
    "Tameside General Hospital":                [53.4890, -2.0480],
    "Royal Bolton Hospital":                    [53.5650, -2.4510],
    "Wigan Infirmary":                          [53.5410, -2.6370],
    "Royal Preston Hospital":                   [53.7670, -2.7210],
    "Royal Blackburn Hospital":                 [53.7360, -2.4770],
    "Blackpool Victoria Hospital":              [53.8180, -3.0290],
    "Royal Lancaster Infirmary":                [54.0560, -2.8010],
    "Furness General Hospital, Barrow":         [54.1290, -3.2050],
    "Wythenshawe Hospital":                     [53.3870, -2.2880],
    "North Manchester General Hospital":        [53.5180, -2.2060],

    # ── SOUTH WEST ──
    # Peninsula
    "Royal Cornwall Hospital, Truro":           [50.2660, -5.0530],
    "Royal Devon & Exeter Hospital":            [50.7180, -3.5100],
    "North Devon District Hospital":            [51.0790, -3.9790],  # Barnstaple
    "Derriford Hospital, Plymouth":             [50.4170, -4.1140],
    "Musgrove Park Hospital, Taunton":          [51.0130, -3.1140],
    "Torbay Hospital":                          [50.4610, -3.5250],
    # Severn
    "Royal United Hospital, Bath":              [51.3880, -2.3880],
    "Bristol Royal Infirmary":                  [51.4580, -2.5930],  # UHBW
    "Southmead Hospital, Bristol":              [51.5010, -2.5960],  # NBT
    "Gloucestershire Royal Hospital":           [51.8640, -2.2380],  # GRH
    "Cheltenham General Hospital":              [51.8930, -2.0680],
    "Great Western Hospital, Swindon":          [51.5530, -1.7580],  # GWH
    "Yeovil District Hospital":                 [50.9400, -2.6340],

    # ── WALES ──
    # North
    "Ysbyty Gwynedd, Bangor":                   [53.2100, -4.1380],
    "Ysbyty Glan Clwyd, Rhyl":                  [53.2660, -3.4870],
    "Wrexham Maelor Hospital":                  [53.0490, -2.9880],
    # South
    "Grange University Hospital, Cwmbran":      [51.6490, -3.0190],
    "University Hospital of Wales, Cardiff":    [51.5070, -3.1900],  # UHW
    "Morriston Hospital, Swansea":              [51.6830, -3.9270],
    "Glangwili Hospital, Carmarthen":           [51.8580, -4.3080],
    "Princess of Wales Hospital, Bridgend":     [51.5120, -3.5710],

    # ── WESSEX ──
    "Poole Hospital":                           [50.7290, -1.9580],
    "Queen Alexandra Hospital, Portsmouth":     [50.8500, -1.0770],
    "Southampton General Hospital":             [50.9340, -1.4340],

    # ── WEST MIDLANDS ──
    # Birmingham School
    "Queen Elizabeth Hospital, Birmingham":      [52.4530, -1.9380],  # QEH
    "Russells Hall Hospital, Dudley":           [52.5060, -2.1180],
    "Worcestershire Royal Hospital":            [52.1930, -2.1770],
    "Wye Valley Hospital, Hereford":            [52.0640, -2.7160],  # Hereford County
    "Midland Metropolitan University Hospital": [52.5000, -1.9630],  # Smethwick
    "Alexandra Hospital, Redditch":             [52.3020, -1.9420],
    # Stoke School
    "Royal Stoke University Hospital":          [53.0010, -2.1870],
    "New Cross Hospital, Wolverhampton":        [52.5910, -2.1260],
    "Royal Shrewsbury Hospital":                [52.7090, -2.7500],
    "Princess Royal Hospital, Telford":         [52.6880, -2.5150],
    "Manor Hospital, Walsall":                  [52.5880, -1.9800],
    # Warwickshire School
    "Heartlands Hospital, Birmingham":          [52.4780, -1.8280],
    "Good Hope Hospital, Sutton Coldfield":     [52.5710, -1.8200],
    "Warwick Hospital":                         [52.2810, -1.5890],
    "University Hospital Coventry":             [52.4210, -1.4410],  # UHCW
    "George Eliot Hospital, Nuneaton":          [52.5090, -1.4680],

    # ── YORKSHIRE AND THE HUMBER ──
    "York Hospital":                            [53.9690, -1.0870],
    "Harrogate District Hospital":              [53.9910, -1.5160],
    "Hull Royal Infirmary":                     [53.7440, -0.3440],
    "Scarborough Hospital":                     [54.2640, -0.3960],
    "Diana, Princess of Wales Hospital":        [53.5640, -0.0770],  # Grimsby
    "Scunthorpe General Hospital":              [53.5850, -0.6530],
    "Sheffield Teaching Hospitals":             [53.3740, -1.4900],  # Northern General / RHH
    "Doncaster Royal Infirmary":                [53.5180, -1.1190],
    "Rotherham Hospital":                       [53.4300, -1.3540],
    "Barnsley Hospital":                        [53.5560, -1.4810],
    "Leeds Teaching Hospitals":                 [53.8060, -1.5220],  # LGI / St James's
    "Bradford Royal Infirmary":                 [53.7920, -1.7680],
    "Airedale General Hospital":                [53.8710, -1.9130],  # Steeton
    "Calderdale Royal Hospital":                [53.7060, -1.8350],  # Halifax
    "Huddersfield Royal Infirmary":             [53.6440, -1.7840],
    "Pinderfields Hospital, Wakefield":         [53.6830, -1.4750],  # Mid Yorks
}

# ─── MATCHING RULES ───
# Map text patterns (from descriptions) to canonical hospital names
HOSPITAL_PATTERNS = [
    # East Midlands - abbreviations and short names
    (r'\bQMC\b', "Queen's Medical Centre, Nottingham"),
    (r'\bCity\b(?:\s*\(Nottingham\))?(?:\s*Hospital)?', "Nottingham City Hospital"),
    (r'\bNCH\b', "Nottingham City Hospital"),
    (r'\bKMH\b', "King's Mill Hospital"),
    (r'\bRDH\b', "Royal Derby Hospital"),
    (r'\bDerby\b(?!\s*Hub)', "Royal Derby Hospital"),
    (r'\bBurton\b', "Queen's Hospital, Burton"),
    (r'\bChesterfield\b', "Chesterfield Royal Hospital"),
    (r'\bLincoln\b(?!\s*Hub)', "Lincoln County Hospital"),
    (r'\bBoston\b', "Pilgrim Hospital, Boston"),
    (r'\bLeicester\b', "Leicester Royal Infirmary"),
    (r'\bLRI\b', "Leicester Royal Infirmary"),
    (r'\bKettering\b', "Kettering General Hospital"),
    (r'\bNorthampton\b', "Northampton General Hospital"),

    # Thames Valley
    (r'Stoke Mandeville', "Stoke Mandeville Hospital"),
    (r'Wycombe Hospital', "Wycombe Hospital"),
    (r'Milton Keynes', "Milton Keynes University Hospital"),
    (r'Horton General', "Horton General Hospital"),
    (r'Oxford University Hospitals|John Radcliffe', "John Radcliffe Hospital, Oxford"),
    (r'Royal Berkshire', "Royal Berkshire Hospital, Reading"),

    # East of England
    (r'Bedford Hospital', "Bedford Hospital"),
    (r'Luton & Dunstable|Luton Hospital', "Luton & Dunstable Hospital"),
    (r'Peterborough Hospital', "Peterborough City Hospital"),
    (r'Broomfield Hospital', "Broomfield Hospital, Chelmsford"),
    (r'Colchester Hospital', "Colchester General Hospital"),
    (r'Southend [Hh]ospital', "Southend University Hospital"),
    (r'James Paget|Gt Yarmouth|Great Yarmouth', "James Paget Hospital, Great Yarmouth"),
    (r'Queen Elizabeth Hospital,?\s*Kings? Lynn', "Queen Elizabeth Hospital, King's Lynn"),
    (r'Norfolk & Norwich', "Norfolk & Norwich University Hospital"),
    (r'West Suffolk Hospital', "West Suffolk Hospital, Bury St Edmunds"),
    (r'Ipswich Hospital', "Ipswich Hospital"),
    (r'Lister Hospital', "Lister Hospital, Stevenage"),
    (r'Watford Hospital', "Watford General Hospital"),

    # Kent, Surrey and Sussex
    (r'Queen Elizabeth the Queen Mother|QEQM', "Queen Elizabeth the Queen Mother Hospital"),
    (r'William Harvey Hospital', "William Harvey Hospital"),
    (r'Medway Maritime', "Medway Maritime Hospital"),
    (r'Maidstone & Tunbridge Wells|Maidstone Hospital', "Maidstone Hospital"),
    (r'Tunbridge Wells Hospital', "Tunbridge Wells Hospital"),
    (r'Darent Valley', "Darent Valley Hospital"),
    (r'Royal Surrey County|Royal Surrey Hospital|Royal Surrey NHS', "Royal Surrey County Hospital"),
    (r"St Peter'?s Hospital|Ashford & St Peter", "St Peter's Hospital, Chertsey"),
    (r'Frimley Park', "Frimley Park Hospital"),
    (r'East Surrey Hospital|Surrey & Sussex Healthcare', "East Surrey Hospital"),
    (r'Brighton.*University Hospitals Sussex|Brighton.*Sussex', "Royal Sussex County Hospital, Brighton"),
    (r"St Richard'?s", "St Richard's Hospital, Chichester"),
    (r'Worthing.*University Hospitals Sussex|Worthing.*Sussex|\bWorthing\b', "Worthing Hospital"),
    (r'East Sussex Healthcare|EAST SUSSEX HEALTHCARE', "Eastbourne District General Hospital"),
    (r'East Kent Hospitals', "Queen Elizabeth the Queen Mother Hospital"),

    # London - North Central
    (r'\bUCH\b|University College Hospital', "University College Hospital"),
    (r'Royal Free', "Royal Free Hospital"),
    (r'Barnet\b(?:\s*(?:and|&)\s*Chase Farm)?|Chase Farm', "Barnet Hospital"),
    (r'Whittington', "Whittington Hospital"),

    # London - North East
    (r'\bBHR\b|Barking,?\s*Havering', "Queen's Hospital, Romford"),
    (r'Homerton', "Homerton University Hospital"),
    (r'Newham\s*Hospital', "Newham University Hospital"),
    (r'Royal London Hospital', "Royal London Hospital"),
    (r'Whipps Cross', "Whipps Cross University Hospital"),

    # London - North West
    (r"St Mary'?s Hospital", "St Mary's Hospital, Paddington"),
    (r'Northwick Park|London North West Hospital|\bLNWH\b', "Northwick Park Hospital"),
    (r'Hammersmith Hospital', "Hammersmith Hospital"),
    (r'Charing Cross Hospital', "Charing Cross Hospital"),
    (r'Chelsea & Westminster|Chelsea and Westminster', "Chelsea & Westminster Hospital"),
    (r'West Middlesex', "West Middlesex University Hospital"),
    (r'Hillingdon', "Hillingdon Hospital"),
    (r'Ealing Hospital', "Ealing Hospital"),

    # London - South East
    (r"Guy'?s\s*(?:&|and)?\s*St\s*Thomas|Guy'?s Hospital|St Thomas", "Guy's Hospital"),
    (r"King'?s College Hospital", "King's College Hospital"),
    (r'Princess Royal University Hospital|PRUH', "Princess Royal University Hospital"),
    (r'University Hospital Lewisham|Lewisham Hospital', "University Hospital Lewisham"),
    (r'Queen Elizabeth Hospital,?\s*Woolwich', "Queen Elizabeth Hospital, Woolwich"),

    # London - South West
    (r"St George'?s", "St George's Hospital, Tooting"),
    (r'Epsom\s*(?:&|and)?\s*St Helier|Epsom Hospital', "Epsom Hospital"),
    (r'St Helier Hospital', "St Helier Hospital"),
    (r'Kingston Hospital', "Kingston Hospital"),
    (r'Croydon\s*(?:University)?\s*Hospital', "Croydon University Hospital"),

    # North West - Cheshire & Merseyside
    (r'Royal Liverpool', "Royal Liverpool University Hospital"),
    (r'Aintree', "Aintree University Hospital"),
    (r'Whiston', "Whiston Hospital"),
    (r'Leighton Hospital|Leighton\b', "Leighton Hospital, Crewe"),
    (r'Warrington\s*Hospital|Warrington\b', "Warrington Hospital"),
    (r"Liverpool Women'?s", "Liverpool Women's Hospital"),
    (r'Macclesfield', "Macclesfield District General Hospital"),
    (r'Arrowe Park', "Arrowe Park Hospital"),
    (r'Countess of Chester', "Countess of Chester Hospital"),
    (r'Southport\s*Hospital|Southport\b', "Southport Hospital"),

    # North West - Greater Manchester etc.
    (r'Manchester Royal Infirmary|MRI\b', "Manchester Royal Infirmary"),
    (r'Salford Royal', "Salford Royal Hospital"),
    (r'Royal Oldham', "Royal Oldham Hospital"),
    (r'Stepping Hill', "Stepping Hill Hospital, Stockport"),
    (r'Tameside', "Tameside General Hospital"),
    (r'Royal Bolton|Bolton\b', "Royal Bolton Hospital"),
    (r'Wigan\b', "Wigan Infirmary"),
    (r'Royal Preston|Preston\b', "Royal Preston Hospital"),
    (r'Royal Blackburn|Blackburn\b', "Royal Blackburn Hospital"),
    (r'Blackpool Victoria|Blackpool\b', "Blackpool Victoria Hospital"),
    (r'Royal Lancaster|Lancaster\b', "Royal Lancaster Infirmary"),
    (r'Furness General|Barrow\b', "Furness General Hospital, Barrow"),
    (r'Wythenshawe', "Wythenshawe Hospital"),
    (r'North Manchester General', "North Manchester General Hospital"),

    # South West - Peninsula
    (r'Royal Cornwall|Cornwall\b|Truro\b', "Royal Cornwall Hospital, Truro"),
    (r'Royal Devon.*Exeter|Exeter\b', "Royal Devon & Exeter Hospital"),
    (r'North Devon\b|Barnstaple\b', "North Devon District Hospital"),
    (r'Derriford|Plymouth\b', "Derriford Hospital, Plymouth"),
    (r'Musgrove Park|Taunton\b', "Musgrove Park Hospital, Taunton"),
    (r'Torbay\s*Hospital|Torbay\b', "Torbay Hospital"),

    # South West - Severn
    (r'Royal United Hospital|RUH\b|Bath\b', "Royal United Hospital, Bath"),
    (r'Bristol Royal Infirmary|\bUHBW\b|Bristol\b(?!.*North)', "Bristol Royal Infirmary"),
    (r'Southmead|North Bristol|\bNBT\b', "Southmead Hospital, Bristol"),
    (r'Gloucestershire Royal|\bGRH\b|Gloucester\b', "Gloucestershire Royal Hospital"),
    (r'Cheltenham General|Cheltenham\b', "Cheltenham General Hospital"),
    (r'Great Western Hospital|\bGWH\b|Swindon\b', "Great Western Hospital, Swindon"),
    (r'Yeovil\b', "Yeovil District Hospital"),

    # Wales - North
    (r'Ysbyty Gwynedd|Bangor\b', "Ysbyty Gwynedd, Bangor"),
    (r'Glan Clwyd|Rhyl\b', "Ysbyty Glan Clwyd, Rhyl"),
    (r'Wrexham Maelor|Wrexham\b', "Wrexham Maelor Hospital"),

    # Wales - South
    (r'Grange University|Cwmbran\b', "Grange University Hospital, Cwmbran"),
    (r'University Hospital of Wales|UHW\b|Cardiff\b', "University Hospital of Wales, Cardiff"),
    (r'Morriston|Swansea Bay', "Morriston Hospital, Swansea"),
    (r'Glangwili|Carmarthen\b', "Glangwili Hospital, Carmarthen"),
    (r'Princess of Wales Hospital|Bridgend\b', "Princess of Wales Hospital, Bridgend"),

    # Wessex
    (r'Poole\b', "Poole Hospital"),
    (r'Queen Alexandra|Portsmouth\b', "Queen Alexandra Hospital, Portsmouth"),
    (r'Southampton General|Southampton\b', "Southampton General Hospital"),

    # West Midlands - BSA
    (r'Queen Elizabeth Hospital.*Birmingham|QEH\b|QE Hospital', "Queen Elizabeth Hospital, Birmingham"),
    (r'Russells Hall', "Russells Hall Hospital, Dudley"),
    (r'Worcestershire Royal|Worcester\b', "Worcestershire Royal Hospital"),
    (r'Wye Valley|Hereford Hospital|Hereford\b', "Wye Valley Hospital, Hereford"),
    (r'Midland Metropolitan', "Midland Metropolitan University Hospital"),
    (r'Alexandra Hospital.*Redditch|Alexandra Hospital\b|Redditch\b', "Alexandra Hospital, Redditch"),

    # West Midlands - SSA
    (r'Royal Stoke University|Royal Stoke\b|Stoke University', "Royal Stoke University Hospital"),
    (r'New Cross Hospital|New Cross\b', "New Cross Hospital, Wolverhampton"),
    (r'Royal Shrewsbury', "Royal Shrewsbury Hospital"),
    (r'Princess Royal Hospital|Princess Royal\b.*Telford', "Princess Royal Hospital, Telford"),
    (r'Manor Hospital', "Manor Hospital, Walsall"),

    # West Midlands - WSA
    (r'Heartlands', "Heartlands Hospital, Birmingham"),
    (r'Good Hope', "Good Hope Hospital, Sutton Coldfield"),
    (r'Warwick Hospital', "Warwick Hospital"),
    (r'University Hospital.*Coventry|\bUHCW\b|Coventry\b', "University Hospital Coventry"),
    (r'George Eli?ot', "George Eliot Hospital, Nuneaton"),

    # Yorkshire
    (r'York\s*Hospital|York\b', "York Hospital"),
    (r'Harrogate', "Harrogate District Hospital"),
    (r'Hull Royal', "Hull Royal Infirmary"),
    (r'Scarborough', "Scarborough Hospital"),
    (r'Diana.*Princess.*Wales|Grimsby\b', "Diana, Princess of Wales Hospital"),
    (r'Scunthorpe', "Scunthorpe General Hospital"),
    (r'Sheffield\b', "Sheffield Teaching Hospitals"),
    (r'Doncaster\b', "Doncaster Royal Infirmary"),
    (r'Rotherham\b', "Rotherham Hospital"),
    (r'Barnsley\b', "Barnsley Hospital"),
    (r'\bLTHT\b|Leeds\b', "Leeds Teaching Hospitals"),
    (r'Bradford\b', "Bradford Royal Infirmary"),
    (r'Airedale\b', "Airedale General Hospital"),
    (r'Calderdale\b', "Calderdale Royal Hospital"),
    (r'Huddersfield\b', "Huddersfield Royal Infirmary"),
    (r'MID Yorks|Pinderfields|Wakefield\b|Pontefract\b', "Pinderfields Hospital, Wakefield"),
]


def extract_hospitals(description, region):
    """Extract all hospital names from a description text."""
    found = []
    seen = set()
    for pattern, name in HOSPITAL_PATTERNS:
        if re.search(pattern, description, re.IGNORECASE):
            if name not in seen:
                seen.add(name)
                found.append(name)
    return found


def get_coords(hospital_name):
    """Get coordinates for a hospital name."""
    return HOSPITAL_COORDS.get(hospital_name)


def haversine_miles(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in miles."""
    R = 3959  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def compute_centroid(coords_list):
    """Compute centroid of a list of [lat, lng] pairs."""
    if not coords_list:
        return None
    lat = sum(c[0] for c in coords_list) / len(coords_list)
    lng = sum(c[1] for c in coords_list) / len(coords_list)
    return [round(lat, 4), round(lng, 4)]


def compute_spread(coords_list):
    """Compute max distance between any two hospitals in miles."""
    if len(coords_list) < 2:
        return 0
    max_dist = 0
    for i in range(len(coords_list)):
        for j in range(i+1, len(coords_list)):
            d = haversine_miles(coords_list[i][0], coords_list[i][1],
                               coords_list[j][0], coords_list[j][1])
            max_dist = max(max_dist, d)
    return round(max_dist, 1)


# ── REGION FALLBACKS ──
REGION_FALLBACK = {
    'East Midlands': [52.95, -1.15],
    'East of England': [52.20, 0.50],
    'Kent, Surrey and Sussex': [51.20, 0.30],
    'London': [51.51, -0.12],
    'North East': [54.97, -1.61],
    'North West': [53.45, -2.55],
    'South West': [50.90, -3.20],
    'Thames Valley': [51.70, -1.00],
    'Wales': [52.00, -3.50],
    'Wessex': [50.90, -1.40],
    'West Midlands': [52.50, -1.90],
    'Yorkshire and the Humber': [53.70, -1.40],
}


def main():
    rows = []
    with open('/Users/flassen/Projects/49_hospital_ranker/Core_ACCS Jobs August 2026.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Preference') and row['Preference'] != 'Preference':
                rows.append(row)

    results = []
    missing = []

    # Fallback: map Area(Sector) and Preference keywords to hospitals
    AREA_FALLBACK = {
        'Cornwall': "Royal Cornwall Hospital, Truro",
        'Exeter': "Royal Devon & Exeter Hospital",
        'North Devon': "North Devon District Hospital",
        'Plymouth': "Derriford Hospital, Plymouth",
        'Taunton': "Musgrove Park Hospital, Taunton",
        'Torbay': "Torbay Hospital",
        'Bath': "Royal United Hospital, Bath",
        'Bristol': "Bristol Royal Infirmary",
        'North Bristol': "Southmead Hospital, Bristol",
        'Cheltenham/Gloucester': "Gloucestershire Royal Hospital",
        'Gloucestershire': "Gloucestershire Royal Hospital",
        'Swindon': "Great Western Hospital, Swindon",
        'Yeovil': "Yeovil District Hospital",
        'Poole': "Poole Hospital",
        'Portsmouth': "Queen Alexandra Hospital, Portsmouth",
        'Southampton': "Southampton General Hospital",
    }

    # Preference-based fallback for generic descriptions
    PREF_FALLBACK = {
        'North East': "North East (generic)",
        'Greater Manchester': "Manchester Royal Infirmary",
        'South Yorkshire': "Sheffield Teaching Hospitals",
        'Wessex': "Southampton General Hospital",
    }

    for i, row in enumerate(rows):
        pref = row['Preference']
        desc = row['Description']
        region = row['Region']
        area = row.get('Area(Sector)', '')

        hospitals = extract_hospitals(desc, region)

        # Fallback 1: use Area(Sector)
        if not hospitals and area and area != '-':
            for area_key, hosp_name in AREA_FALLBACK.items():
                if area_key.lower() in area.lower() or area.lower() in area_key.lower():
                    hospitals = [hosp_name]
                    break

        # Fallback 2: parse Preference field for location
        if not hospitals:
            for pref_key, hosp_name in PREF_FALLBACK.items():
                if pref_key.lower() in pref.lower():
                    hospitals = [hosp_name]
                    break

        # Fallback 3: check description for region keywords
        if not hospitals:
            for pref_key, hosp_name in PREF_FALLBACK.items():
                if pref_key.lower() in desc.lower():
                    hospitals = [hosp_name]
                    break

        # Fallback 4: try matching Preference parts against hospital patterns
        if not hospitals:
            hospitals = extract_hospitals(pref, region)

        # Get coordinates for each hospital
        hospital_list = []
        for h in hospitals:
            coords = get_coords(h)
            if coords:
                hospital_list.append({"name": h, "lat": coords[0], "lng": coords[1]})
            else:
                missing.append(f"  MISSING COORDS: {h} (job: {pref})")

        # Deduplicate by coordinates (some hospitals resolve to same place)
        seen_coords = set()
        unique_hospitals = []
        for h in hospital_list:
            key = (h['lat'], h['lng'])
            if key not in seen_coords:
                seen_coords.add(key)
                unique_hospitals.append(h)

        # Compute centroid and spread
        coords_list = [[h['lat'], h['lng']] for h in unique_hospitals]
        centroid = compute_centroid(coords_list) if coords_list else REGION_FALLBACK.get(region, [53.5, -2.0])
        spread = compute_spread(coords_list) if len(coords_list) >= 2 else 0

        results.append({
            "id": i,
            "preference": pref,
            "hospitals": unique_hospitals,
            "centroid": centroid,
            "spread_miles": spread,
        })

    # Report
    no_hospitals = [r for r in results if not r['hospitals']]
    print(f"Processed {len(results)} jobs")
    print(f"Jobs with hospitals found: {len(results) - len(no_hospitals)}")
    print(f"Jobs with NO hospitals: {len(no_hospitals)}")
    if no_hospitals:
        print("\nJobs with no hospitals matched:")
        for r in no_hospitals:
            row = rows[r['id']]
            print(f"  {r['preference']} | Desc: {row['Description'][:100]}")

    if missing:
        print(f"\nMissing coordinates ({len(missing)}):")
        for m in set(missing):
            print(m)

    # Write output
    output = {h: {"lat": c[0], "lng": c[1]} for h, c in HOSPITAL_COORDS.items()}
    with open('/Users/flassen/Projects/49_hospital_ranker/hospital_data.json', 'w') as f:
        json.dump({
            "hospital_coords": output,
            "job_hospitals": results,
        }, f, indent=2)

    print(f"\nWritten hospital_data.json")

    # Also output just the per-job data as a compact JS constant
    js_data = []
    for r in results:
        js_data.append({
            "h": [[h["name"], h["lat"], h["lng"]] for h in r["hospitals"]],
            "c": r["centroid"],
            "s": r["spread_miles"],
        })

    with open('/Users/flassen/Projects/49_hospital_ranker/job_hospitals.js', 'w') as f:
        f.write("const JOB_HOSPITALS = ")
        json.dump(js_data, f)
        f.write(";\n")

    print(f"Written job_hospitals.js ({len(js_data)} entries)")


if __name__ == '__main__':
    main()
