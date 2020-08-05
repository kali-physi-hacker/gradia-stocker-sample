from django import forms

number_input = forms.NumberInput(attrs={"style": "width: 50px"})
text_input = forms.TextInput(attrs={"size": 1})
longer_text_input = forms.TextInput(attrs={"size": 2})
text_area = forms.Textarea(attrs={"style": "width: 100px; height: 50px"})


class StoneForm(forms.ModelForm):
    class Meta:
        widgets = {
            "color": text_input,
            "grader_1_color": text_input,
            "grader_2_color": text_input,
            "grader_3_color": text_input,
            "clarity": longer_text_input,
            "grader_1_clarity": longer_text_input,
            "grader_2_clarity": longer_text_input,
            "grader_3_clarity": longer_text_input,
            "fluo": text_input,
            "culet": text_input,
            "stone_id": forms.TextInput(attrs={"size": 8}),
            "sequence_number": number_input,
            "carats": number_input,
            "inclusion_remarks": text_area,
            "grader_1_inclusion": text_area,
            "grader_2_inclusion": text_area,
            "grader_3_inclusion": text_area,
            "rejection_remarks": text_area,
            "table_pct": number_input,
            "pavilion_depth_pct": number_input,
            "total_depth_pct": number_input,
        }
