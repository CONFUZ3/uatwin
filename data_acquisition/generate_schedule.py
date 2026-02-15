import json, random
random.seed(42)

BUILDINGS = [
    "South Lawn Office Building","University of Alabama School of Law","Moody Music Building",
    "University Medical Center","Bryant-Jordan Hall","University Hall","Capital Hall",
    "Bryce Main","Smart Communities and Innovation Building","Cyber Hall","Tom Barnes Hall",
    "Psychology Building","McMillan Building","Tom Bevill Building","Shelby Hall",
    "North Engineering Research Center","H.M. Comer Hall","Science and Engineering Complex",
    "Math and Science Building","Walter Bryan Jones Hall","Hardaway Hall",
    "South Engineering Research Center","Houser Hall","B.B. Comer Hall","Woods Hall",
    "Hardaway Hall Annex","Garland Hall","Clark Hall","Oliver-Barnard Hall",
    "Presidents Hall","Rowand Johnson Hall","English Building","Alston Hall","ten Hoor Hall",
    "Hewson Hall","Frederick R. Maxwell Hall","Archie Wade Hall","Little Hall","East Annex",
    "Reese Phifer Hall","Rose Administration Building","Angelo Bruno Business Library",
    "Carmichael Hall","Autherine Lucy Hall","Tuomey Hall","Gallalee Hall","Russell Hall",
    "Honors Hall","Mary Harmon Bryant Hall","Lloyd Hall","Gordon Palmer Hall","Bryant Hall",
    "Farrah Hall","McLure Education Library"
]

DEPTS = [
    "Computer Science","Geography","History","Physics","Mathematics","English",
    "Psychology","Economics","Mechanical Engineering","Civil Engineering","Philosophy",
    "Political Science","Biological Sciences","Chemistry","Art History",
    "Communication Studies","Sociology","Education","Music","Nursing",
    "Environmental Science","Data Science","Electrical Engineering","Accounting"
]

TITLES = {
    "Computer Science": ["Intro to Programming","Data Structures","Algorithms","Artificial Intelligence","Web Development","Database Systems","Machine Learning","Computer Networks"],
    "Geography": ["Human Geography","Physical Geography","GIS Foundations","Urban Planning","Cartography","Remote Sensing","Spatial Analysis","Climate Science"],
    "Mathematics": ["Calculus I","Calculus II","Linear Algebra","Differential Equations","Probability","Statistics","Number Theory","Abstract Algebra"],
    "Physics": ["General Physics I","General Physics II","Quantum Mechanics","Thermodynamics","Electromagnetism","Astrophysics","Optics","Modern Physics"],
    "Chemistry": ["General Chemistry I","General Chemistry II","Organic Chemistry","Biochemistry","Analytical Chemistry","Physical Chemistry"],
    "English": ["Composition I","Composition II","British Literature","American Literature","Creative Writing","Shakespeare","Technical Writing"],
    "Psychology": ["Intro Psychology","Social Psychology","Abnormal Psychology","Developmental Psychology","Cognitive Neuroscience","Research Methods"],
    "History": ["World History I","World History II","US History","Civil War Era","Ancient Greece","Modern Europe","African History"],
    "Economics": ["Microeconomics","Macroeconomics","Econometrics","International Trade","Game Theory","Labor Economics"],
    "Biological Sciences": ["General Biology I","General Biology II","Genetics","Microbiology","Ecology","Physiology","Evolutionary Biology"],
    "Mechanical Engineering": ["Dynamics","Thermodynamics I","Fluid Mechanics","Machine Design","Heat Transfer","Materials Science"],
    "Civil Engineering": ["Statics","Structural Analysis","Geotechnical Engineering","Transportation Engineering","Water Resources"],
    "Philosophy": ["Intro to Philosophy","Ethics","Logic","Ancient Philosophy","Existentialism"],
    "Political Science": ["US Government","International Relations","Comparative Politics","Political Theory","Public Policy"],
    "Art History": ["Ancient Art","Renaissance Art","Modern Art","Asian Art","Women in Art"],
    "Communication Studies": ["Public Speaking","Interpersonal Communication","Media Effects","Rhetoric","Crisis Communication"],
    "Sociology": ["Intro to Sociology","Social Inequality","Criminology","Urban Sociology","Globalization"],
    "Education": ["Foundations of Education","Educational Psychology","Special Education","Curriculum Design"],
    "Music": ["Music Theory I","Music Theory II","Music History","Composition","Performance"],
    "Nursing": ["Anatomy & Physiology","Pharmacology","Nursing Fundamentals","Clinical Practice"],
    "Environmental Science": ["Environmental Science I","Ecology","Conservation Biology","Sustainability"],
    "Data Science": ["Intro to Data Science","Statistical Learning","Big Data Analytics","Data Visualization"],
    "Electrical Engineering": ["Circuits I","Circuits II","Digital Logic","Signals and Systems","Electromagnetics"],
    "Accounting": ["Financial Accounting","Managerial Accounting","Auditing","Tax Accounting"]
}

DAYS_PATTERNS = [
    ["Mon","Wed","Fri"],
    ["Tue","Thu"],
    ["Mon","Wed"],
    ["Tue","Thu"],
    ["Mon","Wed","Fri"],
    ["Fri"]
]

START_TIMES = [
    "08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30",
    "12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30",
    "16:00","16:30","17:00","17:30","18:00","18:30","19:00"
]

PROFS = [
    "Dr. Smith","Dr. Johnson","Dr. Williams","Dr. Brown","Dr. Jones",
    "Dr. Garcia","Dr. Miller","Dr. Davis","Dr. Rodriguez","Dr. Martinez",
    "Dr. Hernandez","Dr. Lopez","Dr. Wilson","Dr. Anderson","Dr. Thomas",
    "Dr. Taylor","Dr. Moore","Dr. Jackson","Dr. Martin","Dr. Lee",
    "Dr. Harris","Dr. Clark","Dr. Lewis","Dr. Walker","Dr. Perez",
    "Dr. Hall","Dr. Young","Dr. Allen","Dr. King","Dr. Wright",
    "Dr. Scott","Dr. Torres","Dr. Hill","Dr. Green","Dr. Adams",
    "Dr. Baker","Dr. Nelson","Dr. Campbell","Dr. Mitchell","Dr. Roberts"
]

schedule = []
ids = set()
for i in range(250):
    dept = random.choice(DEPTS)
    titles = TITLES.get(dept, [dept + " Seminar"])
    title = random.choice(titles)
    num = random.randint(100, 499)
    prefix = dept[:2].upper()
    cid = prefix + str(num)
    while cid in ids:
        num = random.randint(100, 499)
        cid = prefix + str(num)
    ids.add(cid)
    
    bldg = random.choice(BUILDINGS)
    room = str(random.randint(1,4)) + str(random.randint(0,4)) + str(random.randint(0,9))
    days = random.choice(DAYS_PATTERNS)
    st = random.choice(START_TIMES)
    dur = 50 if len(days) == 3 else (75 if len(days) == 2 else 150)
    h, m = map(int, st.split(":"))
    em = m + dur
    eh = h + (em // 60)
    em = em % 60
    et = str(eh).zfill(2) + ":" + str(em).zfill(2)
    cap = random.choice([30, 40, 45, 50, 60, 80, 100, 120, 150, 200, 300])
    enr = int(cap * random.uniform(0.35, 0.98))
    
    schedule.append({
        "id": cid,
        "title": cid + ": " + title,
        "building": bldg,
        "room": room,
        "days": days,
        "startTime": st,
        "endTime": et,
        "enrollment": enr,
        "capacity": cap,
        "instructor": random.choice(PROFS),
        "department": dept
    })

with open("e:/cursor/uatwin/web_app/data/ua_class_schedule.json", "w") as f:
    json.dump(schedule, f, indent=2)

buildings_used = set(c["building"] for c in schedule)
print("Generated", len(schedule), "courses across", len(buildings_used), "buildings")
