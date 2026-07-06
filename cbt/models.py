from django.db import models

class Question(models.Model):
    class Category(models.TextChoices):
        FUNDAMENTALS_OF_NURSING = 'fundamentals_of_nursing', 'Fundamentals of Nursing'
        MEDICAL_SURGICAL_NURSING = 'medical_surgical_nursing', 'Medical-Surgical Nursing'
        ANATOMY_AND_PHYSIOLOGY = 'anatomy_and_physiology', 'Anatomy and Physiology'
        PHARMACOLOGY = 'pharmacology', 'Pharmacology'
        MICROBIOLOGY_AND_PARASITOLOGY = 'microbiology_and_parasitology', 'Microbiology and Parasitology'
        COMMUNITY_HEALTH_NURSING = 'community_health_nursing', 'Community Health Nursing'
        MATERNAL_AND_CHILD_HEALTH = 'maternal_and_child_health', 'Maternal and Child Health'
        MENTAL_HEALTH_PSYCHIATRIC_NURSING = 'mental_health_psychiatric_nursing', 'Mental Health/Psychiatric Nursing'
        NUTRITION = 'nutrition', 'Nutrition'
        NURSING_RESEARCH = 'nursing_research', 'Nursing Research'
        NURSING_EDUCATION_AND_ADMINISTRATION = 'nursing_education_and_administration', 'Nursing Education and Administration'
        PROFESSIONAL_ETHICS_AND_JURISPRUDENCE = 'professional_ethics_and_jurisprudence', 'Professional Ethics and Jurisprudence'

    text = models.TextField()
    category = models.CharField(max_length=60, choices=Category.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['category', 'text']

    def __str__(self):
        return self.text


class Option(models.Model):
    class CorrectOption(models.TextChoices):
        A = 'a', 'A'
        B = 'b', 'B'
        C = 'c', 'C'
        D = 'd', 'D'

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='option')
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=CorrectOption.choices)
    rationale = models.TextField(blank=True, null=True, help_text='Explanation for why the correct answer is right')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
        ordering = ['question']

    def __str__(self):
        return f"Options for: {self.question.text[:50]}..."

