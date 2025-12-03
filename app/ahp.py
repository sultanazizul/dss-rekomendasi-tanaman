import numpy as np
from typing import List, Dict
from app.models import Crop, Recommendation, MatchDetails

class AHPCalculator:
    def __init__(self):
        # Criteria: pH, Rain, Temp, Sun, Irrigation, Soil
        # Order: [pH, Rain, Temp, Sun, Irrigation, Soil]
        self.criteria = ["ph", "rain", "temp", "sun", "irrigation", "soil"]
        
        # Default Pairwise Comparison Matrix (Saaty Scale 1-9)
        # This is a simplified example. In a real scenario, this should be adjustable or derived from expert input.
        # 1: Equal importance, 3: Moderate importance, 5: Strong importance, etc.
        
        # Assumptions:
        # - Water (Rain + Irrigation) is very critical.
        # - Soil type and pH are critical.
        # - Temp and Sun are important but maybe slightly less than water/soil for general suitability (debatable).
        
        # Matrix shape (6x6)
        #       pH   Rain Temp Sun  Irr  Soil
        # pH    1    1/3  3    3    1/3  1
        # Rain  3    1    5    5    1    3
        # Temp  1/3  1/5  1    1    1/5  1/3
        # Sun   1/3  1/5  1    1    1/5  1/3
        # Irr   3    1    5    5    1    3
        # Soil  1    1/3  3    3    1/3  1
        
        self.pairwise_matrix = np.array([
            [1.0, 1/3, 3.0, 3.0, 1/3, 1.0], # pH
            [3.0, 1.0, 5.0, 5.0, 1.0, 3.0], # Rain
            [1/3, 1/5, 1.0, 1.0, 1/5, 1/3], # Temp
            [1/3, 1/5, 1.0, 1.0, 1/5, 1/3], # Sun
            [3.0, 1.0, 5.0, 5.0, 1.0, 3.0], # Irrigation
            [1.0, 1/3, 3.0, 3.0, 1/3, 1.0]  # Soil
        ])
        
        self.weights = self._calculate_weights()
        self.cr = self._calculate_consistency_ratio()

    def _calculate_weights(self) -> Dict[str, float]:
        """
        Calculate priority vector (weights) using the Eigenvector method (approx by normalizing columns).
        """
        # Normalize the matrix (divide each cell by the sum of its column)
        column_sums = self.pairwise_matrix.sum(axis=0)
        normalized_matrix = self.pairwise_matrix / column_sums
        
        # Calculate the average of each row to get the weights
        weights_array = normalized_matrix.mean(axis=1)
        
        # Map back to criteria names
        return dict(zip(self.criteria, weights_array))

    def _calculate_consistency_ratio(self) -> float:
        """
        Calculate Consistency Ratio (CR) to ensure the matrix is logical.
        """
        n = len(self.criteria)
        # Calculate Lambda Max
        # Multiply original matrix by weights vector
        weights_vector = np.array(list(self.weights.values()))
        weighted_sum_vector = self.pairwise_matrix.dot(weights_vector)
        
        # Divide by weights to get consistency vector
        consistency_vector = weighted_sum_vector / weights_vector
        
        lambda_max = consistency_vector.mean()
        
        # Consistency Index (CI)
        ci = (lambda_max - n) / (n - 1)
        
        # Random Index (RI) for n=6 is 1.24
        ri = 1.24
        
        if ri == 0:
            return 0.0
            
        cr = ci / ri
        return cr

    def calculate_match_score(self, user_val: float, min_val: float, max_val: float, is_categorical: bool = False, crop_val: str = None) -> float:
        """
        Calculate how well the user condition matches the crop requirement.
        Returns a score between 0.0 and 1.0.
        """
        if is_categorical:
            # Simple exact match for categorical (Soil Type)
            # In a more advanced version, we could have partial matches (e.g. Loam matches Sandy Loam partially)
            if str(user_val).lower() in str(crop_val).lower() or str(crop_val).lower() in str(user_val).lower():
                return 1.0
            return 0.0
            
        # For numerical ranges
        # If within range, score 1.0
        # If outside, decay the score based on distance
        
        if min_val <= user_val <= max_val:
            return 1.0
        
        # Calculate distance to nearest boundary
        dist = min(abs(user_val - min_val), abs(user_val - max_val))
        
        # Define a tolerance threshold (e.g., 20% of the range width or a fixed value)
        # Let's use a simple linear decay. If it's too far, score drops to 0.
        # Example: pH range 6-7. User has 5. Distance 1.
        # Let's say tolerance is 1.0 unit for pH.
        
        # Dynamic tolerance based on the parameter type?
        # Simplified approach:
        # pH tolerance: 1.0
        # Rain tolerance: 500 mm
        # Temp tolerance: 5 C
        # Sun/Irrigation (0-1 scale): 0.3
        
        # This is a bit hacky, ideally passed as config.
        # We'll infer from the magnitude of values.
        
        range_width = max_val - min_val
        if range_width == 0: range_width = 1 # Avoid div by zero
        
        # Heuristic: Allow deviation up to 50% of the range width or specific absolute values
        tolerance = range_width * 0.5
        
        if dist > tolerance:
            return 0.0
            
        return 1.0 - (dist / tolerance)

    def rank_crops(self, user_inputs: Dict[str, any], crops: List[Crop]) -> List[Recommendation]:
        recommendations = []
        
        for crop in crops:
            # Calculate match score for each criterion
            
            # pH
            s_ph = self.calculate_match_score(user_inputs['ph'], crop.ph_min, crop.ph_max)
            
            # Rain
            s_rain = self.calculate_match_score(user_inputs['rain'], crop.rain_min, crop.rain_max)
            
            # Temp
            s_temp = self.calculate_match_score(user_inputs['temp'], crop.temp_min, crop.temp_max)
            
            # Sun (Categorical in DB but mapped to 0-1 in user input)
            # We need to map crop.sun_requirement (Low/Med/High) to 0-1
            sun_map = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
            crop_sun_val = sun_map.get(crop.sun_requirement, 0.6)
            # Treat as a small range around the value
            s_sun = self.calculate_match_score(user_inputs['sun'], crop_sun_val - 0.2, crop_sun_val + 0.2)
            
            # Irrigation
            irr_map = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
            crop_irr_val = irr_map.get(crop.irrigation_need, 0.6)
            s_irr = self.calculate_match_score(user_inputs['irrigation'], crop_irr_val - 0.2, crop_irr_val + 0.2)
            
            # Soil
            s_soil = self.calculate_match_score(user_inputs['soil'], 0, 0, is_categorical=True, crop_val=crop.soil_type)
            
            # Calculate weighted sum (AHP Score)
            # Score = Sum(Weight_i * Score_i)
            
            final_score = (
                self.weights['ph'] * s_ph +
                self.weights['rain'] * s_rain +
                self.weights['temp'] * s_temp +
                self.weights['sun'] * s_sun +
                self.weights['irrigation'] * s_irr +
                self.weights['soil'] * s_soil
            )
            
            match_details = MatchDetails(
                ph=s_ph,
                rain=s_rain,
                temp=s_temp,
                sun=s_sun,
                irrigation=s_irr,
                soil=s_soil
            )
            
            recommendations.append(Recommendation(
                crop_name=crop.name,
                score=round(final_score, 4),
                match_details=match_details
            ))
            
        # Sort by score descending
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return recommendations
