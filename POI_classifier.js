const turf = require("@turf/turf");

function squaredDistance(a, b) {
  if (!a || !b || a.length < 2 || b.length < 2) return Infinity; // Handle invalid input
  const dx = a[0] - b[0];
  const dy = a[1] - b[1];
  return dx * dx + dy * dy;
}

function findFarthestNodesOptimized(coords) {
  if (!coords || coords.length < 2) {
    return [coords[0] || null, coords[1] || coords[0] || null];
  }

  let minLat = Infinity, maxLat = -Infinity;
  let minLon = Infinity, maxLon = -Infinity;
  let minLatNode = null, maxLatNode = null;
  let minLonNode = null, maxLonNode = null;

  for (const coord of coords) {
    if (coord && coord.length >= 2) {
      const lat = coord[1];
      const lon = coord[0];

      if (lat < minLat) { minLat = lat; minLatNode = coord; }
      if (lat > maxLat) { maxLat = lat; maxLatNode = coord; }
      if (lon < minLon) { minLon = lon; minLonNode = coord; }
      if (lon > maxLon) { maxLon = lon; maxLonNode = coord; }
    }
  }

  if (!minLatNode || !maxLatNode || !minLonNode || !maxLonNode) {
    return [coords[0], coords[1] || coords[0]]; // Fallback for degenerate cases
  }

  const distLat = squaredDistance(minLatNode, maxLatNode);
  const distLon = squaredDistance(minLonNode, maxLonNode);

  const latDiff = Math.abs(maxLat - minLat);
  const lonDiff = Math.abs(maxLon - minLon);
  const tolerance = 1e-9; 

  if (latDiff > lonDiff + tolerance) {
    return [minLatNode, maxLatNode];
  } else if (lonDiff > latDiff + tolerance) {
    return [minLonNode, maxLonNode];
  } else {
    return [coords[0], coords[coords.length - 1]];
  }
}

function findReferenceNode(coords) {
  if (!coords || coords.length === 0) return null;
  if (coords.length === 1) return coords[0];

  const [nodeA, nodeB] = findFarthestNodesOptimized(coords);

  if (!nodeA || !nodeB) return coords[0]; 

  const latA = nodeA[1];
  const lonA = nodeA[0];
  const zA = nodeA.length > 2 ? nodeA[2] : -Infinity; 

  const latB = nodeB[1];
  const lonB = nodeB[0];
  const zB = nodeB.length > 2 ? nodeB[2] : -Infinity; 

  if (latA < latB) return nodeA;
  if (latB < latA) return nodeB;
  if (lonA < lonB) return nodeA;
  if (lonB < lonA) return nodeB;
  return zA < zB ? nodeA : nodeB;
}

function orderCoords(coords, refNode) {
  if (!coords || coords.length <= 2) return coords || [];
  if (!refNode) return [...coords]; 

  const remaining = coords.filter(c => c !== refNode);
  const ordered = [refNode];
  let current = refNode;

  while (remaining.length) {
    let closestIdx = -1;
    let closestDist = Infinity;

    for (let i = 0; i < remaining.length; i++) {
      const dist = squaredDistance(current, remaining[i]);
      if (dist < closestDist) {
        closestDist = dist;
        closestIdx = i;
      }
    }

    if (closestIdx !== -1) {
      ordered.push(remaining[closestIdx]);
      current = remaining.splice(closestIdx, 1)[0];
    } else {
      break; 
    }
  }

  return ordered;
}

function interpolateAlongLineImproved(coords, perc) {
  if (!coords || coords.length === 0) return null;
  if (coords.length === 1) return coords[0];
  if (perc <= 0) return coords[0];
  if (perc >= 1) return coords[coords.length - 1];

  const refNode = findReferenceNode(coords);
  const orderedCoords = orderCoords(coords, refNode);

  if (orderedCoords.length < 2) return refNode || coords[0] || null;

  const line = turf.lineString(orderedCoords);
  const length = turf.length(line, { units: "meters" });

  if (length <= 0) {
    return orderedCoords[0]; 
  }

  try {
    const along = turf.along(line, length * perc, { units: "meters" });
    return along.geometry.coordinates;
  } catch (error) {
    console.error("Error in interpolateAlongLine:", error);
    return null;
  }
}

function validatePercentage(perc) {
  const numPerc = parseFloat(perc) / 100; 
  return isNaN(numPerc) || numPerc < 0 || numPerc > 1
    ? { valid: false, reason: `Invalid PERCFRREF: ${perc}` }
    : { valid: true, value: numPerc };
}

function determineThreshold(linkProperties) {
  const isUrban = String(linkProperties.URBAN).toUpperCase() === "Y";
  const isHighway = ["1", "2"].includes(String(linkProperties.FUNC_CLASS));

  if (isHighway) return 70;
  if (isUrban) return 10;
  return 40;
}

function checkNameMismatch(linkName, poiName) {
  const normalizedLinkName = String(linkName || "").trim().toLowerCase();
  const normalizedPoiName = String(poiName || "").trim().toLowerCase();
  return normalizedLinkName !== normalizedPoiName && normalizedLinkName !== "" && normalizedPoiName !== "";
}

function classifySinglePOIImproved(poi, links) {
  const props = poi.properties || {};
  const linkId = String(props.LINK_ID);
  const link = links.find(l => String(l.properties.link_id) === linkId);

  if (!link) {
    return { ...poi, properties: { ...props, _scenario: 1, _reason: "No matching link found" } };
  }

  try {
    const percResult = validatePercentage(props.PERCFRREF);
    if (!percResult.valid) {
      return { ...poi, properties: { ...props, _scenario: 1, _reason: percResult.reason } };
    }
    const perc = percResult.value;

    const expectedCoord = interpolateAlongLineImproved(link.geometry.coordinates, perc);
    if (!expectedCoord) {
      return { ...poi, properties: { ...props, _scenario: 1, _reason: "Could not interpolate along line" } };
    }

    const poiCoords = poi.geometry && poi.geometry.coordinates;
    if (!poiCoords || poiCoords.length < 2) {
      return { ...poi, properties: { ...props, _scenario: 1, _reason: "Invalid POI coordinates" } };
    }

    const dist = turf.distance(turf.point(poiCoords), turf.point(expectedCoord), { units: "meters" });
    const threshold = determineThreshold(link.properties);
    const nameMismatch = checkNameMismatch(link.properties.ST_NAME, props.ST_NAME);
    const multiDigitMismatch =
      link.properties.MULTIDIGIT !== undefined &&
      props.MULTIDIGIT !== undefined &&
      String(link.properties.MULTIDIGIT).trim().toLowerCase() !== String(props.MULTIDIGIT).trim().toLowerCase();

    let scenario = 4;
    let reason = "Valid position and attributes";

    if (dist > threshold) {
      scenario = 2;
      reason = `Offset ${dist.toFixed(1)}m > ${threshold}m threshold`;
    } else if (nameMismatch) {
      scenario = 3;
      reason = `Name mismatch (link: "${link.properties.ST_NAME}", POI: "${props.ST_NAME}")`;
    } 

    return {
      ...poi,
      properties: {
        ...props,
        _scenario: scenario,
        _reason: reason,
        _debug: {
          expected: expectedCoord,
          distance: dist,
          threshold,
          isUrban: String(link.properties.URBAN).toUpperCase() === "Y",
          isHighway: ["1", "2"].includes(String(link.properties.FUNC_CLASS)),
        },
      },
    };
  } catch (err) {
    console.error("Error classifying POI:", err);
    return { ...poi, properties: { ...props, _scenario: 1, _reason: `Processing error: ${err.message}` } };
  }
}

function classifyPOIsImproved(pois, links) {
  if (!Array.isArray(pois)) {
    console.error("Error: 'pois' must be an array.");
    return [];
  }
  if (!Array.isArray(links)) {
    console.error("Error: 'links' must be an array.");
    return pois.map(poi => ({ ...poi, properties: { ...poi.properties, _scenario: 1, _reason: "Links data not provided" } }));
  }

  return pois.map(poi => classifySinglePOIImproved(poi, links));
}

module.exports = classifyPOIsImproved;
