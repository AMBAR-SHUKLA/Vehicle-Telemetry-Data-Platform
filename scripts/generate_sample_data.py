"""
Sample Data Generator for Vehicle Telemetry Platform
Generates realistic test data for vehicles and telemetry
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict

class DataGenerator:
    """Generate sample data for testing the platform"""
    
    # San Francisco Bay Area coordinates
    SF_CENTER = (37.7749, -122.4194)
    RADIUS = 0.5  # Approximately 50km radius
    
    VEHICLE_TYPES = ["truck", "van", "car"]
    VEHICLE_STATUSES = ["idle", "in_transit", "maintenance"]
    
    def __init__(self, num_vehicles: int = 10):
        self.num_vehicles = num_vehicles
        self.vehicles = []
    
    def random_coordinates(self, center, radius):
        """Generate random coordinates within radius of center"""
        lat_offset = (random.random() - 0.5) * 2 * radius
        lon_offset = (random.random() - 0.5) * 2 * radius
        return (center[0] + lat_offset, center[1] + lon_offset)
    
    def generate_vehicles(self) -> List[Dict]:
        """Generate sample vehicle data"""
        vehicles = []
        
        for i in range(self.num_vehicles):
            lat, lon = self.random_coordinates(self.SF_CENTER, self.RADIUS)
            
            vehicle = {
                "vehicle_id": f"V{i+1:03d}",
                "vehicle_type": random.choice(self.VEHICLE_TYPES),
                "capacity": random.uniform(500, 2000),  # kg
                "current_lat": round(lat, 6),
                "current_lon": round(lon, 6),
                "status": random.choice(self.VEHICLE_STATUSES)
            }
            vehicles.append(vehicle)
        
        self.vehicles = vehicles
        return vehicles
    
    def generate_telemetry(self, vehicle_id: str, num_records: int = 10) -> List[Dict]:
        """Generate telemetry records for a vehicle"""
        telemetry = []
        
        # Get vehicle's current position
        vehicle = next((v for v in self.vehicles if v["vehicle_id"] == vehicle_id), None)
        if not vehicle:
            return []
        
        start_lat, start_lon = vehicle["current_lat"], vehicle["current_lon"]
        
        for i in range(num_records):
            # Simulate movement
            lat_change = random.uniform(-0.01, 0.01)
            lon_change = random.uniform(-0.01, 0.01)
            
            record = {
                "vehicle_id": vehicle_id,
                "latitude": round(start_lat + lat_change * i, 6),
                "longitude": round(start_lon + lon_change * i, 6),
                "speed": round(random.uniform(0, 100), 2),  # km/h
                "fuel_level": round(random.uniform(20, 100), 2)  # percentage
            }
            telemetry.append(record)
        
        return telemetry
    
    def generate_delivery_locations(self, num_locations: int = 20) -> List[Dict]:
        """Generate delivery destination coordinates"""
        locations = []
        
        for i in range(num_locations):
            lat, lon = self.random_coordinates(self.SF_CENTER, self.RADIUS)
            
            location = {
                "location_id": f"L{i+1:03d}",
                "name": f"Delivery Point {i+1}",
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "demand": random.uniform(50, 500),  # kg
                "time_window_start": f"{random.randint(8, 12)}:00",
                "time_window_end": f"{random.randint(14, 18)}:00"
            }
            locations.append(location)
        
        return locations
    
    def generate_road_network(self, num_nodes: int = 50) -> Dict:
        """
        Generate a sample road network graph
        Returns: Graph structure with nodes and edges
        """
        nodes = []
        edges = []
        
        # Generate nodes (intersections/locations)
        for i in range(num_nodes):
            lat, lon = self.random_coordinates(self.SF_CENTER, self.RADIUS)
            nodes.append({
                "node_id": i,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6)
            })
        
        # Generate edges (roads) - connect each node to 3-5 random neighbors
        for i in range(num_nodes):
            num_connections = random.randint(3, 5)
            possible_neighbors = [j for j in range(num_nodes) if j != i]
            neighbors = random.sample(possible_neighbors, min(num_connections, len(possible_neighbors)))
            
            for neighbor in neighbors:
                # Calculate approximate distance
                lat1, lon1 = nodes[i]["latitude"], nodes[i]["longitude"]
                lat2, lon2 = nodes[neighbor]["latitude"], nodes[neighbor]["longitude"]
                distance = ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5 * 111  # Approximate km
                
                edges.append({
                    "from_node": i,
                    "to_node": neighbor,
                    "distance": round(distance, 2),
                    "travel_time": round(distance / random.uniform(30, 60), 2),  # minutes
                    "traffic_factor": round(random.uniform(0.8, 1.5), 2)  # Traffic multiplier
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "num_nodes": num_nodes,
                "num_edges": len(edges),
                "center": self.SF_CENTER
            }
        }
    
    def save_to_json(self, data: Dict, filename: str):
        """Save generated data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Saved to {filename}")


def main():
    """Generate all sample data"""
    print("🎲 Generating sample data...\n")
    
    generator = DataGenerator(num_vehicles=10)
    
    # Generate vehicles
    print("Generating vehicles...")
    vehicles = generator.generate_vehicles()
    generator.save_to_json({"vehicles": vehicles}, "sample_vehicles.json")
    
    # Generate telemetry for each vehicle
    print("\nGenerating telemetry data...")
    all_telemetry = []
    for vehicle in vehicles:
        telemetry = generator.generate_telemetry(vehicle["vehicle_id"], num_records=20)
        all_telemetry.extend(telemetry)
    generator.save_to_json({"telemetry": all_telemetry}, "sample_telemetry.json")
    
    # Generate delivery locations
    print("\nGenerating delivery locations...")
    locations = generator.generate_delivery_locations(num_locations=25)
    generator.save_to_json({"locations": locations}, "sample_locations.json")
    
    # Generate road network
    print("\nGenerating road network...")
    network = generator.generate_road_network(num_nodes=100)
    generator.save_to_json(network, "sample_road_network.json")
    
    # Generate sample API requests
    print("\nGenerating API request examples...")
    api_examples = {
        "register_vehicle": {
            "method": "POST",
            "url": "http://localhost:8000/api/v1/vehicles/",
            "body": vehicles[0]
        },
        "submit_telemetry": {
            "method": "POST",
            "url": "http://localhost:8000/api/v1/telemetry/",
            "body": all_telemetry[0]
        },
        "optimize_routes": {
            "method": "POST",
            "url": "http://localhost:8000/api/v1/optimize/routes",
            "body": {
                "vehicles": [v["vehicle_id"] for v in vehicles[:5]],
                "destinations": locations[:10],
                "optimization_type": "minimize_distance"
            }
        }
    }
    generator.save_to_json(api_examples, "api_examples.json")
    
    print("\n" + "="*50)
    print("✓ Sample data generation complete!")
    print("="*50)
    print("\nGenerated files:")
    print("  - sample_vehicles.json (10 vehicles)")
    print("  - sample_telemetry.json (200 telemetry records)")
    print("  - sample_locations.json (25 delivery locations)")
    print("  - sample_road_network.json (100 nodes, ~400 edges)")
    print("  - api_examples.json (Sample API requests)")
    print("\nUse these files to test your API and algorithms!")


if __name__ == "__main__":
    main()
