from django.db import models
from django import forms

class RunCommentForm(forms.Form):
    run_id = forms.CharField(max_length=100)
    content = forms.CharField(max_length=5000, required=False)

class run_comment(forms.Form):
    text = forms.CharField(max_length=5000)

class run_search_form( forms.Form ):

    def __init__(self, list, *args, **kwargs):
        super( run_search_form, self).__init__(*args, **kwargs)
        self.fields['mode'] = forms.ChoiceField( choices=list, required=False )

    detectors = [ ("tpc", "TPC"), ("muon_veto", "Muon Veto"), ("all", "All")]
    detector = forms.ChoiceField(choices=detectors, required=False, label="Detector")
    startdate = forms.DateField(required = False, label = "Start Date", widget=forms.DateInput)
    enddate   = forms.DateField(required = False, label = "End Date", widget=forms.DateInput)
    GoodRuns  = forms.BooleanField(label = "Only good runs", required=False)
    custom = forms.CharField( max_length=1000, required = False )
