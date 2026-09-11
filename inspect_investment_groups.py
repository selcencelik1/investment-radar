from app.database.investment_repository import get_all_investment_records
from app.matching.investment_grouper import group_investment_records


def main() -> None:
    records = get_all_investment_records()
    groups = group_investment_records(records)

    grouped = [
        group
        for group in groups
        if len(group.members) > 1
    ]

    member_ids = [
        member.id
        for group in groups
        for member in group.members
    ]

    original_ids = [record.id for record in records]

    # Her kaynak kaydı tam olarak bir grupta bulunmalı.
    assert sorted(member_ids) == sorted(original_ids)
    assert len(member_ids) == len(set(member_ids))

    print(f"Ham kaynak kaydı: {len(records)}")
    print(f"Gösterilecek grup: {len(groups)}")
    print(f"Çok kaynaklı grup: {len(grouped)}")
    print(f"Korunan kaynak kaydı: {len(member_ids)}")

    for group in grouped:
        print(f"\n{group.primary.startup_name}")
        print(f"Durum: {group.match_status}")

        for member in group.members:
            print(
                f"  ID={member.id} | "
                f"{member.reporting_period} | "
                f"Aşama={member.investment_stage}"
            )

    print("\nVeritabanında değişiklik yapılmadı.")


if __name__ == "__main__":
    main()