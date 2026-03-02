import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skin_diseases.settings')
django.setup()

from skin_diseases import models

def seed_diseases():
    diseases = [
        {
            "name": "Actinic Keratoses",
            "desc": "Precancerous skin lesions caused by sun damage.",
            "symp": "Rough, scaly patches on sun-exposed areas.",
            "prec": "Use sunscreen, wear protective clothing, and avoid peak sun hours."
        },
        {
            "name": "Basal Cell Carcinoma",
            "desc": "A type of skin cancer that begins in the basal cells.",
            "symp": "A pearly or waxy bump, or a flat, flesh-colored scar-like lesion.",
            "prec": "Surgical removal and regular monitoring by a dermatologist."
        },
        {
            "name": "Benign Keratosis-like Lesions",
            "desc": "Non-cancerous skin growths that can appear waxy or scaly.",
            "symp": "Tan, brown, or black growths with a 'stuck-on' look.",
            "prec": "Generally harmless, but can be removed if irritated."
        },
        {
            "name": "Dermatofibroma",
            "desc": "Common non-cancerous skin growths often found on lower legs.",
            "symp": "Small, firm red-to-brown bumps; may feel like a hard pea under the skin.",
            "prec": "Harmless; no treatment usually required unless painful."
        },
        {
            "name": "Melanocytic Nevi",
            "desc": "Common moles; clusters of pigmented cells.",
            "symp": "Small, dark brown spots; can be flat or raised.",
            "prec": "Monitor for changes in shape, size, or color (ABCDE rule)."
        },
        {
            "name": "Melanoma",
            "desc": "The most serious type of skin cancer, developing in melanocytes.",
            "symp": "A change in an existing mole or a new, unusual-looking growth.",
            "prec": "Immediate medical consultation and surgical intervention."
        },
        {
            "name": "Vascular Lesions",
            "desc": "Skin conditions involving blood vessels (e.g., angiomas).",
            "symp": "Red or purple spots or patches on the skin.",
            "prec": "Usually benign, but can be treated with laser therapy for aesthetics."
        }
    ]

    print("Seeding disease table...")
    for d in diseases:
        obj, created = models.Disease.objects.update_or_create(
            disease_name=d['name'],
            defaults={
                'description': d['desc'],
                'symptoms': d['symp'],
                'precautions': d['prec']
            }
        )
        if created:
            print(f"Added: {d['name']}")
        else:
            print(f"Updated: {d['name']}")

    print("Seeding complete.")

if __name__ == "__main__":
    seed_diseases()
