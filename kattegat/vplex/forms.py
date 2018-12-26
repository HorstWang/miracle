from django import forms

class create_investigation_form(forms.Form):
    sr_id = forms.IntegerField()
    oracle_sr_id = forms.IntegerField()
    owner = forms.CharField(max_length=50)
    description = forms.CharField(max_length=1000)
    
class cd_log_attach_form(forms.Form):
#   remote_log_path = forms.CharField(widget= forms.Textarea, max_length=1000)
    cdlog_file = forms.FileField()

class search_component_form(forms.Form):
    cdlog_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    component_type = forms.ChoiceField(choices=[('SV', 'Storage view'), ('I', 'Initiator'), ('P', 'Port'), ('VV', 'Virtual volume'), ('SV', 'Storage volume')]) 
    key = forms.CharField(max_length=100)

class date_span_picker_form(forms.Form):
    start_date_time = forms.DateTimeField(widget=forms.TextInput(attrs={ 'class':'datepicker' }))
    end_date_time = forms.DateTimeField(widget=forms.TextInput(attrs={ 'class':'datepicker' }))