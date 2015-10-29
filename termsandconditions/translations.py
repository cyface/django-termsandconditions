from modeltranslation.translator import translator, TranslationOptions
from .models import TermsAndConditions


class TermsAndConditionsTranslationOptions(TranslationOptions):
    fields = ('name', 'text', 'info')
translator.register(TermsAndConditions, TermsAndConditionsTranslationOptions)
