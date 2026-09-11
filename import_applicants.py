from app.database.applicant_repository import save_applicants
from app.importers.applicant_importer import load_applicants_from_csv


applicants = load_applicants_from_csv(
    "data/sample_applicants.csv"
)


created_count, updated_count, removed_count = (
    save_applicants(applicants)
)

print(f"Applicant records found in CSV: {len(applicants)}")
print(f"New applications created: {created_count}")
print(f"Existing applications updated: {updated_count}")
print(f"Applications removed: {removed_count}")

print(f"Applicant records found in CSV: {len(applicants)}")
print(f"New applicants saved: {saved_count}")