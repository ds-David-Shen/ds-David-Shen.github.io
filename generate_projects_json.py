import pdfplumber
import re
import json

# Path to your PDF resume
pdf_file_path = "ds-David-Shen.github.io/assets/pdf/Resume.pdf"

# Extract text from PDF
with pdfplumber.open(pdf_file_path) as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)

# Preprocessing: Remove artifacts like (cid:...) and clean broken lines
text = re.sub(r"\(cid:\d+\)", "", text)  # Remove (cid:...) artifacts
lines = text.split("\n")
cleaned_lines = []

for line in lines:
    if line.strip():  # Remove empty lines
        if cleaned_lines and not line.startswith(("Projects", "–", "|")) and not re.match(r".+ \| .+ [A-Za-z0-9– ]+$", line):
            cleaned_lines[-1] += f" {line.strip()}"
        else:
            cleaned_lines.append(line.strip())

# Extract the Projects section
projects_section = []
inside_projects = False
for line in cleaned_lines:
    if line == "Projects":
        inside_projects = True
    elif inside_projects:
        if line.startswith("Technical Skills"):  # End of Projects section
            break
        projects_section.append(line)

# Combine projects into a single string for regex parsing
projects_text = "\n".join(projects_section)

# Regex to extract project data
project_regex = re.compile(
    r"^(?P<title>.+?) \| (?P<technologies>.+?) (?P<date>[A-Za-z]+ [0-9]{4} – [A-Za-z]+ [0-9]{4}|[A-Za-z]+ [0-9]{4} – Present)\s*"
    r"((?:– .*?(?:\n|$))+)",  # Match multiline details
    re.MULTILINE
)

# Extract projects
projects = []
for match in project_regex.finditer(projects_text):
    title = match.group("title").strip()
    technologies = match.group("technologies").strip()
    date = match.group("date").strip()
    raw_details = match.group(4).strip().split("\n")
    details = [
        detail.strip().lstrip("– ") for detail in raw_details
        if not detail.startswith("Technical Skills")  # Stop overflow into unrelated sections
    ]

    # If the last detail contains "Technical Skills," trim it
    if details and "Technical Skills" in details[-1]:
        details[-1] = details[-1].split("Technical Skills")[0].strip()

    projects.append({
        "title": title,
        "technologies": technologies,
        "date": date,
        "details": details
    })

# Debug: Print extracted projects
print("Extracted Projects:")
for project in projects:
    print(project)

# Save to JSON
json_file_path = "ds-David-Shen.github.io/assets/json/projects.json"
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(projects, json_file, indent=2)

print(f"Extracted projects saved to {json_file_path}.")
