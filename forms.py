from django import forms

units_of_measure = [ '']
class QueueEntryForm(forms.Form):
    name = forms.CharField(label = "Queue Task Name", max_length=100, required=True)
    upload_file = forms.FileField(label = "Upload GeoJSON Points", widget = forms.FileInput(attrs={'accept': '.geojson'}))
    buffers = forms.CharField(label = "Buffer Distances in Degrees (Comma Seperated)", max_length = 100, required = True)

