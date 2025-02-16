import xml.etree.ElementTree as ET
import sys

def truncate_coordinates(coordinates, decimal_places):
    if decimal_places is None:
        return coordinates
    truncated_coords = []
    for coord in coordinates.split():
        lon, lat, *rest = coord.split(',')
        lon = f"{float(lon):.{decimal_places}f}"
        lat = f"{float(lat):.{decimal_places}f}"
        truncated_coords.append(','.join([lon, lat] + rest))
    return ' '.join(truncated_coords)

def remove_duplicates(input_file, output_file, decimal_places=None):
    # Parse the KML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Define namespaces
    namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Find the Document element
    document = root.find('.//kml:Document', namespaces)

    # Find all placemarks
    placemarks = document.findall('.//kml:Placemark', namespaces)

    # Dictionary to store unique placemarks
    unique_placemarks = {}
    parent_map = {c: p for p in tree.iter() for c in p}

    for placemark in placemarks:
        coordinates = placemark.find('.//kml:coordinates', namespaces).text.strip()
        truncated_coords = truncate_coordinates(coordinates, decimal_places)
        if truncated_coords not in unique_placemarks:
            unique_placemarks[truncated_coords] = placemark

    # Remove all placemarks from the document
    for placemark in placemarks:
        parent = parent_map[placemark]
        parent.remove(placemark)

    # Add unique placemarks back to the document
    for placemark in unique_placemarks.values():
        document.append(placemark)

    # Register namespace to avoid ns0 prefix
    ET.register_namespace('', 'http://www.opengis.net/kml/2.2')

    # Write the new KML file
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python remove_duplicates.py <input_kml_file> <output_kml_file> [decimal_places]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    decimal_places = int(sys.argv[3]) if len(sys.argv) == 4 else None

    remove_duplicates(input_file, output_file, decimal_places)
    print(f"Duplicates removed. Output saved to {output_file}")
