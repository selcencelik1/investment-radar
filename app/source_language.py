# Labels and keywords that occur verbatim in Turkish source reports.
# They are isolated here so domain and presentation modules remain English.
UNKNOWN_INVESTOR_LABELS = {
    "açıklanmayan yatırımcı",
    "açıklanmayan yatırımcılar",
    "undisclosed investor",
    "undisclosed investors",
}

MISSING_INVESTOR_VALUES = {
    "",
    "na",
    "n/a",
    "açıklanmadı",
    "undisclosed",
}

SOURCE_DIACRITIC_TRANSLATION = str.maketrans({
    "â": "a",
    "î": "i",
    "û": "u",
})

INSTITUTION_KEYWORDS = (
    "gsyf",
    "gsyo",
    "fund",
    "fon",
    "ventures",
    "venture",
    "capital",
    "portföy",
    "portfoy",
    "investment",
    "investments",
)

INDIVIDUAL_INVESTOR_KEYWORDS = (
    "private investor",
    "özel yatırımcı",
)

ELIGIBLE_STAGE_LABELS = {
    "tohum aşaması",
    "tohum",
    "seri a",
}

EXCLUDED_STAGE_LABELS = {
    "satın alım",
    "satın alma",
    "halka arz",
    "geç aşama",
    "seri b",
    "seri c",
}

KPMG_REQUIRED_HTML_HEADERS = {
    "Hedef Şirket",
    "Sektör",
    "Yatırımcı",
    "İşlem Değeri ($m)",
}

KPMG_STAGE_HTML_HEADERS = {
    "Yatırım Aşaması",
    "İşlem Tipi",
}

KPMG_HTML_HEADER_ALIASES = {
    "Girişim": "Hedef Şirket",
    "Yatırımcı Merkezi": "Yatırımcı Ülkesi",
    "İşlem Değeri (m$)": "İşlem Değeri ($m)",
}

KPMG_HTML_FIELDS = {
    "ranking": "Sıralama",
    "startup_name": "Hedef Şirket",
    "sector": "Sektör",
    "investors": "Yatırımcı",
    "investor_countries": "Yatırımcı Ülkesi",
    "share_percentage": "Hisse (%)",
    "deal_amount": "İşlem Değeri ($m)",
    "investment_stage": "Yatırım Aşaması",
    "transaction_type": "İşlem Tipi",
}

NOT_DISCLOSED_LABEL = "açıklanmadı"

STARTUP_NAME_ALLOWED_CHARACTERS_PATTERN = r"[^0-9a-zçğıöşü]+"

LOCALIZED_COMPANY_SUFFIXES = (
    " anonim şirketi",
    " limited şirketi",
    " ltd şti",
    " a ş",
    " a s",
    " ltd",
    " şti",
)

REPORT_QUARTER_PATTERNS = {
    "Q1": (
        r"(?:\b1\s*\.\s*çeyrek|\bbirinci\s+çeyrek|"
        r"\bilk\s+çeyrek|\bq1\b)"
    ),
    "Q2": r"(?:\b2\s*\.\s*çeyrek|\bikinci\s+çeyrek|\bq2\b)",
    "Q3": r"(?:\b3\s*\.\s*çeyrek|\büçüncü\s+çeyrek|\bq3\b)",
    "Q4": r"(?:\b4\s*\.\s*çeyrek|\bdördüncü\s+çeyrek|\bq4\b)",
}

ANNUAL_REPORT_EXPRESSIONS = (
    "yıllık",
    "yıl sonu",
    "full year",
)

REVIEW_STATUS_TRANSLATIONS = {
    "İncelenecek": "To review",
    "İnceleniyor": "In progress",
    "Görüşüldü": "Contacted",
    "Arşivlendi": "Archived",
}

SOURCE_VALUE_TRANSLATIONS = {
    "Eğitim Teknolojisi": "Education Technology",
    "Gıda Teknolojisi": "Food Technology",
    "Sağlık Teknolojisi": "Health Technology",
    "Oyun": "Gaming",
    "Erken Aşama": "Early Stage",
    "Satın Alım": "Acquisition",
    "Tohum Aşaması": "Seed Stage",
    "Türkiye": "Turkey",
    "Açıklanmadı": "Not disclosed",
    "Kurala göre gruplandı": "Grouped by matching rules",
    "Tek kaynak kaydı": "Single source record",
    "Belirsiz eşleşme — ayrı tutuldu": (
        "Ambiguous match — kept separate"
    ),
    "Kaynak tutarının sayı biçimi belirsiz; sayısal tutara dönüştürülmedi.": (
        "The source amount format is ambiguous and was not converted "
        "to a numeric value."
    ),
}

INVESTOR_LABEL_TRANSLATIONS = {
    "Açıklanmayan Yatırımcılar": "Undisclosed Investors",
    "Açıklanmayan Yatırımcı": "Undisclosed Investor",
}
TRUE_VALUE_LABELS = {
    "true",
    "yes",
    "1",
    "evet",
    "evet.",
}

FALSE_VALUE_LABELS = {
    "false",
    "no",
    "0",
    "hayır",
    "hayır.",
}

TURKISH_APPLICANT_COLUMN_ALIASES = {
    "Adınız Soyadınız": "applicant_full_name",
    "Unvanınız": "applicant_title",
    "Telefon Numaranız": "applicant_phone",
    "E-mail Adresiniz": "applicant_email",
    "LinkedIn Profiliniz": "applicant_linkedin_url",

    "Girişiminizin Adı / Firmanızın Unvanı": "startup_name",
    "Faaliyet Alanı / Sektör / NACE Kodu": "sector_nace_code",
    "Girişiminizin / Firmanızın Durumu": "company_legal_status",
    "Girişiminizin merkezi hangi ülkede?": "headquarters_country",
    "Kuruluş Tarihi": "founding_date",
    "Girişiminizin / Firmanızın Açıklaması": "startup_description",
    (
        "Ürününüzün / Hizmetinizin Ele Aldığı Problem "
        "ve Çözüm Konuları"
    ): "problem_solution",
    "İş ve Gelir Modeli": "business_revenue_model",
    "Girişiminizin Aşaması": "startup_stage",
    "Girişiminizin İnternet Sayfası": "website_url",
    (
        "Ürününüzü deneyimleyebileceğimiz internet "
        "sayfası, demo, uygulama linki?"
    ): "product_demo_url",
    "Logo": "logo_url",
    (
        "Girişiminizin Tanıtım Sunumuna Ait Link"
    ): "pitch_deck_url",
    (
        "Daha önce herhangi bir girişim programına "
        "katıldınız mı?"
    ): "previous_program_participation",

    (
        "Yönetim ekibiniz kaç kişiden oluşmaktadır?"
    ): "management_team_size",
    (
        "Bize yönetim ekibinizden bahseder misiniz?"
    ): "management_team_description",
    (
        "Ekibinizin teknik ya da sektör bilgisi adına "
        "uzmanlığından bahseder misiniz?"
    ): "team_expertise",

    "Mevcut Müşteri Sayısı": "active_customer_count",
    "MRR Değeriniz?": "mrr_usd",
    "ARR Değeriniz?": "arr_usd",
    "Aylık Geliriniz?": "monthly_revenue_usd",
    "Yıllık Geliriniz?": "annual_revenue_usd",
    "Daha önce yatırım aldınız mı?": "previously_funded",
    "Yatırım beklentiniz ne kadar?": "investment_expectation_usd",
    (
        "Yatırımı nasıl değerlendirmeyi planlıyorsunuz?"
    ): "investment_use_plan",

    (
        "Daha önce havayolu ya da havacılık/seyahat "
        "sektöründe çalışan bir firmayla çalıştınız mı?"
    ): "aviation_sector_experience",
    (
        "Daha önce birlikte çalıştığınız şirketleri ya da "
        "endüstri temsilcilerini detaylandırabilir misiniz?"
    ): "aviation_partners",
    (
        "Daha önce Türk Hava Yolları ya da iştirak "
        "şirketleriyle herhangi bir iletişiminiz, "
        "iş birliğiniz oldu mu?"
    ): "thy_group_relationship",
    (
        "Türk Hava Yolları ile nasıl bir partnerlik "
        "yapmak istiyorsunuz?"
    ): "desired_thy_partnership",
    (
        "Eklemek ya da sormak istediğiniz başka bir "
        "konu var mı?"
    ): "additional_notes",
}