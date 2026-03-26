"""
Enhanced Severity Analysis Module
Provides detailed problem identification and clinical findings
"""

def analyze_severity_indicators_detailed(symptoms_data):
    """Enhanced severity analysis with comprehensive problem identification"""
    indicators = {
        "fever_level": "none",
        "fever_severity": "none",
        "duration_concern": "low",
        "symptom_count": 0,
        "red_flags": [],
        "severity_score": 0,
        "risk_factors": [],
        "symptom_clusters": [],
        "problems_identified": [],
        "detailed_analysis": {},
        "clinical_findings": []
    }
    
    # DETAILED FEVER ANALYSIS
    if 'fever' in symptoms_data and symptoms_data['fever'] == 'yes':
        fever_temp = symptoms_data.get('fever_followup', '')
        if 'Below 100' in fever_temp:
            indicators['fever_level'] = 'low'
            indicators['fever_severity'] = 'MILD'
            indicators['severity_score'] += 2
            indicators['problems_identified'].append('✓ Low-grade fever (Below 100°F / 37.8°C)')
            indicators['detailed_analysis']['fever'] = {
                'temperature': 'Below 100°F (37.8°C)',
                'classification': 'Low-grade fever',
                'concern_level': 'Minimal',
                'likely_causes': ['Viral infection', 'Minor illness'],
                'action_needed': 'Monitor and home care'
            }
            indicators['clinical_findings'].append('Temperature: Mild elevation (subfebrile)')
        elif '100-102' in fever_temp:
            indicators['fever_level'] = 'moderate'
            indicators['fever_severity'] = 'MODERATE'
            indicators['severity_score'] += 4
            indicators['problems_identified'].append('⚠️ Moderate fever (100-102°F / 37.8-38.9°C)')
            indicators['detailed_analysis']['fever'] = {
                'temperature': '100-102°F (37.8-38.9°C)',
                'classification': 'Moderate fever',
                'concern_level': 'Moderate',
                'likely_causes': ['Viral/Bacterial infection', 'Inflammatory response'],
                'action_needed': 'Monitor closely, antipyretics recommended'
            }
            indicators['clinical_findings'].append('Temperature: Moderate elevation (febrile)')
        elif 'Above 102' in fever_temp:
            indicators['fever_level'] = 'high'
            indicators['fever_severity'] = 'SEVERE'
            indicators['severity_score'] += 7
            indicators['problems_identified'].append('🚨 HIGH FEVER (Above 102°F / 38.9°C) - URGENT')
            indicators['red_flags'].append('🚨 HIGH FEVER >102°F - Immediate medical attention needed')
            indicators['detailed_analysis']['fever'] = {
                'temperature': 'Above 102°F (38.9°C)',
                'classification': 'High fever / Hyperpyrexia',
                'concern_level': 'HIGH - Urgent',
                'likely_causes': ['Severe infection', 'Sepsis risk'],
                'action_needed': 'URGENT medical care',
                'complications': ['Dehydration', 'Seizures', 'Organ stress']
            }
            indicators['clinical_findings'].append('Temperature: Severe (hyperpyrexia) - URGENT')
        elif "Haven't measured" in fever_temp:
            indicators['fever_level'] = 'unknown'
            indicators['fever_severity'] = 'MODERATE'
            indicators['severity_score'] += 3
            indicators['problems_identified'].append('⚠️ Fever present but NOT measured')
            indicators['risk_factors'].append('Temperature not measured - severity unknown')
            indicators['clinical_findings'].append('Subjective fever - needs measurement')
    
    # DURATION ANALYSIS
    duration = symptoms_data.get('duration', '')
    if 'Less than 24 hours' in duration:
        indicators['duration_concern'] = 'low'
        indicators['severity_score'] += 1
        indicators['problems_identified'].append('✓ Acute onset (<24 hours)')
        indicators['detailed_analysis']['duration'] = {
            'timeframe': '<24 hours',
            'classification': 'Acute',
            'prognosis': 'Good - early stage'
        }
    elif '1-3 days' in duration:
        indicators['duration_concern'] = 'moderate'
        indicators['severity_score'] += 2
        indicators['problems_identified'].append('⚠️ Symptoms for 1-3 days')
        indicators['detailed_analysis']['duration'] = {
            'timeframe': '1-3 days',
            'classification': 'Short-term',
            'prognosis': 'Should improve with care'
        }
    elif '3-7 days' in duration:
        indicators['duration_concern'] = 'high'
        indicators['severity_score'] += 4
        indicators['problems_identified'].append('⚠️ PROLONGED symptoms (3-7 days)')
        indicators['risk_factors'].append('Symptoms persisting - evaluation needed')
    elif 'More than a week' in duration:
        indicators['duration_concern'] = 'critical'
        indicators['severity_score'] += 6
        indicators['problems_identified'].append('🚨 CHRONIC symptoms (>7 days) - URGENT')
        indicators['red_flags'].append('🚨 Prolonged >7 days - Medical evaluation REQUIRED')
    
    # SYMPTOM ANALYSIS
    other_symptoms = symptoms_data.get('other_symptoms', [])
    if isinstance(other_symptoms, list):
        symptom_list = [s for s in other_symptoms if s != 'None']
        indicators['symptom_count'] = len(symptom_list)
        indicators['severity_score'] += len(symptom_list)
        
        if symptom_list:
            indicators['problems_identified'].append(f'✓ {len(symptom_list)} additional symptoms present')
            for symptom in symptom_list:
                indicators['clinical_findings'].append(f'• {symptom}')
        
        # Respiratory cluster
        resp = [s for s in symptom_list if s in ['Cough', 'Sore throat']]
        if resp:
            indicators['symptom_clusters'].append(f'RESPIRATORY: {", ".join(resp)}')
            indicators['problems_identified'].append(f'🫁 Respiratory symptoms: {", ".join(resp)}')
        
        # GI cluster
        gi = [s for s in symptom_list if s in ['Nausea/Vomiting', 'Diarrhea']]
        if gi:
            indicators['symptom_clusters'].append(f'GI: {", ".join(gi)}')
            indicators['problems_identified'].append(f'🤢 GI symptoms: {", ".join(gi)}')
            indicators['severity_score'] += 2
            
            if 'Nausea/Vomiting' in gi and 'Diarrhea' in gi:
                indicators['problems_identified'].append('🚨 HIGH DEHYDRATION RISK')
                indicators['red_flags'].append('⚠️ Dehydration risk - vomiting + diarrhea')
                indicators['severity_score'] += 3
        
        # Systemic cluster
        systemic = [s for s in symptom_list if s in ['Headache', 'Chills', 'Body aches']]
        if systemic:
            indicators['symptom_clusters'].append(f'SYSTEMIC: {", ".join(systemic)}')
            indicators['problems_identified'].append(f'💪 Systemic symptoms: {", ".join(systemic)}')
    
    # RESPIRATORY DISTRESS
    respiratory = symptoms_data.get('respiratory', [])
    if isinstance(respiratory, list):
        if 'Difficulty breathing' in respiratory:
            indicators['problems_identified'].append('🚨🚨 CRITICAL: DIFFICULTY BREATHING - EMERGENCY')
            indicators['red_flags'].append('🚨🚨 EMERGENCY: Difficulty breathing - CALL 911')
            indicators['severity_score'] += 10
            indicators['clinical_findings'].append('🚨 RESPIRATORY DISTRESS - EMERGENCY')
        
        if 'Shortness of breath' in respiratory:
            indicators['problems_identified'].append('⚠️ Shortness of breath')
            indicators['red_flags'].append('⚠️ Dyspnea - urgent evaluation needed')
            indicators['severity_score'] += 5
        
        if 'Wheezing' in respiratory:
            indicators['problems_identified'].append('⚠️ Wheezing - airway narrowing')
            indicators['risk_factors'].append('Wheezing - bronchospasm present')
            indicators['severity_score'] += 3
    
    # PAIN ANALYSIS
    if symptoms_data.get('pain') == 'yes':
        pain_locations = symptoms_data.get('pain_followup', [])
        if isinstance(pain_locations, list) and pain_locations:
            indicators['problems_identified'].append(f'💢 Pain in: {", ".join(pain_locations)}')
            
            if 'Chest' in pain_locations:
                indicators['problems_identified'].append('🚨🚨 CRITICAL: CHEST PAIN - EMERGENCY')
                indicators['red_flags'].append('🚨🚨 CHEST PAIN - CALL 911 IMMEDIATELY')
                indicators['severity_score'] += 10
                indicators['clinical_findings'].append('🚨 CHEST PAIN - CARDIAC EMERGENCY')
            
            if 'Stomach' in pain_locations:
                indicators['problems_identified'].append('⚠️ Abdominal pain')
                indicators['risk_factors'].append('Abdominal pain - monitor closely')
                indicators['severity_score'] += 2
            
            if 'Head' in pain_locations:
                indicators['problems_identified'].append('✓ Headache (likely fever-related)')
                indicators['severity_score'] += 1
    
    # EXPOSURE
    if symptoms_data.get('exposure') == 'yes':
        indicators['problems_identified'].append('⚠️ Recent exposure to sick individuals/travel')
        indicators['risk_factors'].append('Exposure history positive')
        indicators['severity_score'] += 2
    
    # MEDICATIONS
    if symptoms_data.get('medication') == 'yes':
        meds = symptoms_data.get('medication_followup', [])
        if isinstance(meds, list) and len(meds) > 0:
            indicators['problems_identified'].append(f'💊 Taking {len(meds)} medication(s): {", ".join(meds)}')
            indicators['risk_factors'].append(f'Current medications: {len(meds)}')
    
    # ADVANCED SEVERITY ASSESSMENT
    score = indicators['severity_score']
    red_flag_count = len(indicators['red_flags'])
    
    # Critical conditions override score
    has_emergency = any('🚨🚨' in flag for flag in indicators['red_flags'])
    has_high_fever = indicators['fever_level'] == 'high'
    has_prolonged = indicators['duration_concern'] == 'critical'
    has_dehydration = any('DEHYDRATION' in p for p in indicators['problems_identified'])
    has_respiratory_distress = any('DIFFICULTY BREATHING' in flag.upper() for flag in indicators['red_flags'])
    
    # CRITICAL: Emergency conditions
    if has_emergency or has_respiratory_distress:
        indicators['overall_severity'] = 'CRITICAL'
        indicators['severity_interpretation'] = '🚨 EMERGENCY - Immediate medical care required'
        indicators['urgency_level'] = 'EMERGENCY'
    # SEVERE: Multiple red flags or high-risk combinations
    elif red_flag_count >= 3 or (has_high_fever and has_prolonged) or (has_high_fever and has_dehydration) or score >= 18:
        indicators['overall_severity'] = 'SEVERE'
        indicators['severity_interpretation'] = '⚠️ Severe condition - Urgent medical attention needed within hours'
        indicators['urgency_level'] = 'HIGH'
    # MODERATE: Some red flags or moderate score
    elif red_flag_count >= 1 or score >= 8 or (indicators['fever_level'] == 'moderate' and indicators['symptom_count'] >= 3):
        indicators['overall_severity'] = 'MODERATE'
        indicators['severity_interpretation'] = '⚠️ Moderate illness - Medical consultation recommended within 24-48 hours'
        indicators['urgency_level'] = 'MEDIUM'
    # MILD: Low score, no red flags
    else:
        indicators['overall_severity'] = 'MILD'
        indicators['severity_interpretation'] = '✓ Minor illness - Home care with monitoring'
        indicators['urgency_level'] = 'LOW'
    
    # CONDITION-SPECIFIC ASSESSMENT
    condition_patterns = []
    
    # Flu-like illness
    if indicators['fever_level'] in ['moderate', 'high'] and indicators['symptom_count'] >= 2:
        systemic = [s for s in indicators.get('symptom_clusters', []) if 'SYSTEMIC' in s]
        if systemic:
            condition_patterns.append('Influenza-like illness')
    
    # Respiratory infection
    if any('RESPIRATORY' in c for c in indicators.get('symptom_clusters', [])):
        if indicators['fever_level'] != 'none':
            condition_patterns.append('Upper respiratory tract infection')
        else:
            condition_patterns.append('Common cold')
    
    # Gastroenteritis
    if any('GI' in c for c in indicators.get('symptom_clusters', [])):
        condition_patterns.append('Gastroenteritis')
    
    # Viral fever
    if indicators['fever_level'] != 'none' and indicators['symptom_count'] <= 2:
        condition_patterns.append('Viral fever')
    
    indicators['likely_conditions'] = condition_patterns if condition_patterns else ['General illness']
    
    # PROBLEM SUMMARY
    indicators['problem_summary'] = {
        'total_problems': len(indicators['problems_identified']),
        'critical_issues': len([p for p in indicators['problems_identified'] if '🚨' in p]),
        'warning_issues': len([p for p in indicators['problems_identified'] if '⚠️' in p]),
        'severity_score': score,
        'severity_level': indicators['overall_severity'],
        'urgency_level': indicators.get('urgency_level', 'MEDIUM'),
        'red_flag_count': red_flag_count,
        'likely_conditions': indicators['likely_conditions']
    }
    
    return indicators
