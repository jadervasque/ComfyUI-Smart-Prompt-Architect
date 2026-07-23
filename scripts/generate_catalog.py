"""Generate the reviewed, original Prompt Architect Catalog V2 data set.

This is an offline authoring tool. The node never runs it and never accesses the
network. Every phrase is assembled from project-owned controlled vocabularies;
external wildcard collections are used only to audit missing taxonomy branches.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

CATALOG_VERSION: Final = "2.0.0"
SCHEMA_VERSION: Final = "2.0"
_ROOT = Path(__file__).resolve().parents[1]
_CATALOG_ROOT = _ROOT / "prompt_architect" / "data" / "catalogs"
_PROFILE_ROOT = _ROOT / "prompt_architect" / "data" / "profiles"
_SLUG = re.compile(r"[^a-z0-9]+")


def _terms(value: str) -> tuple[str, ...]:
    result = tuple(item.strip() for item in value.split("|") if item.strip())
    if len(result) != 8:
        raise ValueError(f"axis must contain exactly eight terms: {value!r}")
    return result


SECONDARY: Final[dict[str, tuple[str, ...]]] = {
    "definition": _terms(
        "softly defined|cleanly outlined|gently tapered|evenly proportioned|"
        "subtly angular|smoothly contoured|distinctly structured|naturally asymmetric"
    ),
    "tone": _terms(
        "neutral undertone|warm undertone|cool undertone|golden undertone|"
        "olive undertone|rose undertone|muted undertone|luminous undertone"
    ),
    "finish": _terms(
        "matte finish|soft sheen|natural luster|textured finish|"
        "brushed finish|polished finish|weathered finish|satin finish"
    ),
    "construction": _terms(
        "precise tailoring|relaxed drape|layered construction|clean seaming|"
        "structured volume|fluid movement|practical detailing|minimal construction"
    ),
    "scale": _terms(
        "delicate scale|compact scale|balanced scale|elongated scale|"
        "broad scale|generous scale|graduated scale|irregular scale"
    ),
    "spatial": _terms(
        "open spatial layout|intimate spatial layout|layered depth|clear sightlines|"
        "enclosed geometry|expansive geometry|asymmetric layout|central organization"
    ),
    "atmospheric": _terms(
        "clear atmosphere|light haze|soft mist|humid air|dry air|"
        "wind-swept air|still air|particulate glow"
    ),
    "light": _terms(
        "low contrast|moderate contrast|high contrast|soft transitions|"
        "crisp transitions|broad falloff|rapid falloff|layered illumination"
    ),
    "camera": _terms(
        "documentary restraint|formal precision|intimate emphasis|spatial context|"
        "graphic geometry|dynamic energy|quiet observation|editorial polish"
    ),
    "motion": _terms(
        "resting movement|measured movement|flowing movement|decisive movement|"
        "suspended movement|rhythmic movement|asymmetric movement|controlled momentum"
    ),
    "expression": _terms(
        "subtle intensity|open warmth|quiet restraint|focused attention|"
        "gentle tension|confident ease|reflective distance|animated energy"
    ),
    "color": _terms(
        "muted saturation|balanced saturation|rich saturation|pale value range|"
        "deep value range|warm color bias|cool color bias|neutral color balance"
    ),
    "era": _terms(
        "faithful period detail|modern reinterpretation|restrained ornament|"
        "functional construction|ceremonial refinement|everyday authenticity|"
        "weathered character|museum-clean finish"
    ),
    "negative": _terms(
        "minor occurrence|repeated occurrence|prominent occurrence|edge occurrence|"
        "background occurrence|subject occurrence|high-frequency occurrence|"
        "composition-wide occurrence"
    ),
}


@dataclass(frozen=True, slots=True)
class PackSpec:
    """One authoring recipe for a segmented pack."""

    pack_id: str
    library: str
    domain: str
    category: str
    primary_name: str
    primary: tuple[str, ...]
    secondary_name: str
    secondary: str
    template: str
    safety: str = "general"
    status: str = "active"
    priority: int = 100
    tags: tuple[str, ...] = ()


def _spec(
    pack_id: str,
    library: str,
    domain: str,
    primary: str,
    secondary: str,
    template: str,
    *,
    category: str | None = None,
    primary_name: str = "family",
    secondary_name: str = "treatment",
    safety: str = "general",
    priority: int = 100,
    tags: tuple[str, ...] = (),
) -> PackSpec:
    return PackSpec(
        pack_id=pack_id,
        library=library,
        domain=domain,
        category=category or library,
        primary_name=primary_name,
        primary=_terms(primary),
        secondary_name=secondary_name,
        secondary=secondary,
        template=template,
        safety=safety,
        priority=priority,
        tags=tags,
    )


SPECS: Final[tuple[PackSpec, ...]] = (
    _spec(
        "identity-subject-type-base",
        "subject-type",
        "identity",
        "adult person|adult woman|adult man|nonbinary adult|adult fashion model|"
        "adult creative professional|adult athlete|adult performing artist",
        "expression",
        "{primary} presented with {secondary}",
        primary_name="adult-subject",
        tags=("base", "adults-only"),
    ),
    _spec(
        "identity-adult-age-base",
        "adult-age",
        "identity",
        "adult in their twenties|adult in their thirties|adult in their forties|"
        "adult in their fifties|adult in their sixties|adult in their seventies|"
        "adult in their eighties|mature adult of unspecified age",
        "definition",
        "{primary}, with {secondary} age characterization",
        primary_name="age-band",
        tags=("base", "adults-only"),
    ),
    _spec(
        "identity-archetype-base",
        "identity-archetype",
        "identity",
        "thoughtful researcher|independent designer|community organizer|experienced artisan|"
        "calm mentor|curious traveler|disciplined performer|inventive entrepreneur",
        "expression",
        "an adult {primary} with {secondary}",
        primary_name="archetype",
        tags=("base", "adults-only"),
    ),
    _spec(
        "identity-face-shape-base",
        "face-shape",
        "identity",
        "oval|round|square|oblong|heart-shaped|diamond-shaped|triangular|pear-shaped",
        "definition",
        "a {secondary} {primary} facial outline",
        primary_name="shape",
        tags=("base",),
    ),
    _spec(
        "identity-facial-structure-base",
        "facial-structure",
        "identity",
        "high cheekbone|low cheekbone|broad jaw|narrow jaw|prominent chin|soft chin|"
        "wide forehead|compact forehead",
        "definition",
        "{secondary} {primary} structure",
        primary_name="structure",
        tags=("base",),
    ),
    _spec(
        "identity-eye-color-base",
        "eye-color",
        "identity",
        "brown|amber|hazel|green|blue|gray|dark brown|blue-green",
        "tone",
        "{primary} eyes with a {secondary}",
        primary_name="hue",
        tags=("base",),
    ),
    _spec(
        "identity-eye-shape-base",
        "eye-shape",
        "identity",
        "almond-shaped|round|deep-set|hooded|upturned|downturned|wide-set|close-set",
        "definition",
        "{secondary} {primary} eyes",
        primary_name="shape",
        tags=("base",),
    ),
    _spec(
        "identity-eyebrows-base",
        "eyebrows",
        "identity",
        "straight|softly arched|high-arched|rounded|angled|full|fine|tapered",
        "definition",
        "{secondary} {primary} eyebrows",
        primary_name="shape",
        tags=("base",),
    ),
    _spec(
        "identity-nose-base",
        "nose",
        "identity",
        "straight bridge|gently curved bridge|broad bridge|narrow bridge|rounded tip|"
        "defined tip|low bridge|high bridge",
        "definition",
        "a {secondary} nose with a {primary}",
        primary_name="structure",
        tags=("base",),
    ),
    _spec(
        "identity-mouth-base",
        "mouth",
        "identity",
        "full upper lip|full lower lip|balanced lips|bow-shaped upper lip|wide mouth|"
        "compact mouth|soft lip contour|defined lip contour",
        "definition",
        "a {secondary} mouth with {primary}",
        primary_name="structure",
        tags=("base",),
    ),
    _spec(
        "identity-skin-tone-base",
        "skin-tone",
        "identity",
        "very deep|deep|medium-deep|medium|medium-light|light|very light|rich brown",
        "tone",
        "{primary} skin with a {secondary}",
        primary_name="value",
        tags=("base",),
    ),
    _spec(
        "identity-skin-texture-base",
        "skin-texture",
        "identity",
        "smooth|fine-pored|visible-pored|softly textured|naturally varied|dewy|matte|"
        "gently weathered",
        "finish",
        "{primary} skin texture with a {secondary}",
        primary_name="texture",
        tags=("base",),
    ),
    _spec(
        "identity-skin-details-base",
        "skin-details",
        "identity",
        "light freckles|dense freckles|beauty marks|fine smile lines|fine forehead lines|"
        "subtle under-eye texture|sun-kissed variation|natural tonal variation",
        "scale",
        "{primary} appearing at a {secondary}",
        primary_name="detail",
        tags=("base",),
    ),
    _spec(
        "identity-distinguishing-features-base",
        "distinguishing-features",
        "identity",
        "subtle facial asymmetry|distinct cheek contour|recognizable brow line|"
        "characteristic smile line|distinctive nose profile|recognizable chin contour|"
        "natural birthmark|small healed scar",
        "definition",
        "{secondary} {primary}",
        primary_name="feature",
        tags=("base",),
    ),
    _spec(
        "hair-color-base",
        "hair-color",
        "hair",
        "black|dark brown|chestnut brown|auburn|copper|golden blonde|ash blonde|silver-gray",
        "tone",
        "{primary} hair with a {secondary}",
        primary_name="hue",
        tags=("base",),
    ),
    _spec(
        "hair-length-base",
        "hair-length",
        "hair",
        "closely cropped|ear-length|chin-length|shoulder-length|collarbone-length|"
        "mid-back-length|waist-length|mixed-length layered",
        "definition",
        "{primary} hair with a {secondary} perimeter",
        primary_name="length",
        tags=("base",),
    ),
    _spec(
        "hair-texture-base",
        "hair-texture",
        "hair",
        "pin-straight|straight|softly wavy|deeply wavy|loose-curly|tight-curly|coily|kinky-coily",
        "definition",
        "{primary} hair with {secondary} strand definition",
        primary_name="texture",
        tags=("base",),
    ),
    _spec(
        "hair-style-base",
        "hair-style",
        "hair",
        "loose natural style|center-parted style|side-parted style|low ponytail|high ponytail|"
        "low bun|braided arrangement|layered crop",
        "construction",
        "a {primary} shaped through {secondary}",
        primary_name="style",
        tags=("base",),
    ),
    _spec(
        "hair-facial-hair-base",
        "facial-hair",
        "hair",
        "clean-shaven finish|light stubble|short boxed beard|full natural beard|trimmed goatee|"
        "defined mustache|mustache and beard combination|closely cropped beard",
        "definition",
        "{primary} with {secondary} edge definition",
        primary_name="style",
        tags=("base",),
    ),
    _spec(
        "body-build-base",
        "body-build",
        "body",
        "slender build|lean build|average build|soft build|athletic build|muscular build|"
        "broad build|full build",
        "definition",
        "an adult with a {secondary} {primary}",
        primary_name="build",
        tags=("base", "adults-only"),
    ),
    _spec(
        "wardrobe-theme-contemporary",
        "wardrobe-theme",
        "wardrobe",
        "contemporary casual|smart casual|minimal modern|creative professional|urban utility|"
        "relaxed tailoring|modern evening|refined everyday",
        "construction",
        "{primary} wardrobe direction with {secondary}",
        primary_name="theme",
        priority=10,
        tags=("base", "contemporary"),
    ),
    _spec(
        "wardrobe-theme-editorial",
        "wardrobe-theme",
        "wardrobe",
        "runway editorial|luxury campaign|avant-garde tailoring|couture-inspired|"
        "conceptual fashion|high-gloss evening|sculptural fashion|monochrome editorial",
        "construction",
        "{primary} wardrobe direction with {secondary}",
        primary_name="theme",
        priority=20,
        tags=("editorial", "fashion"),
    ),
    _spec(
        "wardrobe-theme-historical",
        "wardrobe-theme",
        "wardrobe",
        "regency-inspired|victorian-inspired|edwardian-inspired|art-deco-inspired|"
        "mid-century-inspired|renaissance-inspired|baroque-inspired|folk-historic-inspired",
        "era",
        "{primary} wardrobe with {secondary}",
        primary_name="period",
        priority=30,
        tags=("historical",),
    ),
    _spec(
        "wardrobe-theme-fantasy",
        "wardrobe-theme",
        "wardrobe",
        "courtly fantasy|woodland fantasy|scholarly fantasy|traveler fantasy|"
        "celestial fantasy|desert fantasy|maritime fantasy|artisan fantasy",
        "construction",
        "{primary} wardrobe with {secondary}",
        primary_name="theme",
        priority=40,
        tags=("fantasy",),
    ),
    _spec(
        "wardrobe-theme-dark",
        "wardrobe-theme",
        "wardrobe",
        "gothic formal|noir evening|dark romantic|weathered occult-inspired|"
        "shadowed ceremonial|somber victorian-inspired|dark woodland|monastic minimal",
        "construction",
        "{primary} wardrobe with {secondary}",
        primary_name="theme",
        safety="dark-atmospheric",
        priority=50,
        tags=("dark", "gothic"),
    ),
    _spec(
        "wardrobe-tops-base",
        "tops",
        "wardrobe",
        "button-front shirt|fine-knit sweater|structured blouse|relaxed t-shirt|"
        "high-neck top|wrap top|tunic|sleeveless shell",
        "construction",
        "a {primary} with {secondary}",
        primary_name="garment",
        tags=("base",),
    ),
    _spec(
        "wardrobe-bottoms-base",
        "bottoms",
        "wardrobe",
        "straight trousers|wide-leg trousers|tapered trousers|tailored shorts|"
        "midi skirt|long skirt|utility trousers|relaxed jeans",
        "construction",
        "{primary} with {secondary}",
        primary_name="garment",
        tags=("base",),
    ),
    _spec(
        "wardrobe-one-piece-base",
        "one-piece",
        "wardrobe",
        "shirt dress|wrap dress|column dress|tailored jumpsuit|utility jumpsuit|"
        "knit dress|a-line dress|structured overall",
        "construction",
        "a {primary} with {secondary}",
        primary_name="garment",
        tags=("base",),
    ),
    _spec(
        "wardrobe-one-piece-mature-fashion",
        "one-piece",
        "wardrobe",
        "elegant slip dress|open-back evening dress|deep-v evening jumpsuit|"
        "fitted cocktail dress|draped halter dress|off-shoulder column dress|"
        "sheer-overlay evening dress|sculpted bodice dress",
        "construction",
        "a non-explicit adult {primary} with {secondary}",
        primary_name="garment",
        safety="fashion-mature",
        priority=30,
        tags=("fashion", "mature"),
    ),
    _spec(
        "wardrobe-outerwear-base",
        "outerwear",
        "wardrobe",
        "single-breasted coat|double-breasted coat|cropped jacket|long cardigan|"
        "utility jacket|trench coat|structured blazer|lightweight parka",
        "construction",
        "a {primary} with {secondary}",
        primary_name="garment",
        tags=("base",),
    ),
    _spec(
        "wardrobe-footwear-base",
        "footwear",
        "wardrobe",
        "low-profile sneakers|lace-up boots|ankle boots|loafers|flat sandals|"
        "block-heel shoes|classic pumps|practical walking shoes",
        "construction",
        "{primary} with {secondary}",
        primary_name="garment",
        tags=("base",),
    ),
    _spec(
        "wardrobe-materials-base",
        "materials",
        "wardrobe",
        "cotton|linen|wool|silk|denim|leather|velvet|technical woven fabric",
        "finish",
        "{primary} material with a {secondary}",
        primary_name="material",
        tags=("base",),
    ),
    _spec(
        "wardrobe-patterns-base",
        "patterns",
        "wardrobe",
        "solid field|fine stripe|wide stripe|small check|large check|geometric repeat|"
        "botanical repeat|abstract tonal pattern",
        "scale",
        "a {primary} at a {secondary}",
        primary_name="pattern",
        tags=("base",),
    ),
    _spec(
        "wardrobe-accessories-base",
        "accessories",
        "wardrobe",
        "structured handbag|crossbody bag|wide belt|narrow belt|silk scarf|"
        "leather gloves|compact umbrella|minimal watch",
        "finish",
        "a {primary} with a {secondary}",
        primary_name="accessory",
        tags=("base",),
    ),
    _spec(
        "wardrobe-jewelry-base",
        "jewelry",
        "wardrobe",
        "small hoop earrings|drop earrings|stud earrings|fine chain necklace|"
        "sculptural necklace|stacked rings|single cuff bracelet|delicate brooch",
        "finish",
        "{primary} with a {secondary}",
        primary_name="jewelry",
        tags=("base",),
    ),
    _spec(
        "wardrobe-headwear-base",
        "headwear",
        "wardrobe",
        "wide-brim hat|soft beanie|structured cap|silk headscarf|felt fedora|"
        "woven sun hat|minimal headband|beret",
        "construction",
        "a {primary} with {secondary}",
        primary_name="headwear",
        tags=("base",),
    ),
    _spec(
        "wardrobe-palette-base",
        "palette",
        "wardrobe",
        "earth neutral|cool neutral|warm neutral|deep jewel|soft pastel|"
        "high-contrast monochrome|muted botanical|sun-washed coastal",
        "color",
        "a {primary} palette with {secondary}",
        primary_name="palette",
        tags=("base",),
    ),
    _spec(
        "performance-expression-base",
        "expression",
        "performance",
        "calm expression|gentle smile|broad smile|thoughtful expression|focused expression|"
        "quietly confident expression|curious expression|serene expression",
        "expression",
        "{primary} carrying {secondary}",
        primary_name="expression",
        tags=("base",),
    ),
    _spec(
        "performance-gaze-base",
        "gaze",
        "performance",
        "direct gaze|off-camera gaze|downward gaze|upward gaze|sideward gaze|"
        "distant gaze|softly focused gaze|intently focused gaze",
        "expression",
        "{primary} with {secondary}",
        primary_name="direction",
        tags=("base",),
    ),
    _spec(
        "performance-head-position-base",
        "head-position",
        "performance",
        "level head position|slight left turn|slight right turn|three-quarter left turn|"
        "three-quarter right turn|gentle upward tilt|gentle downward tilt|profile position",
        "definition",
        "{primary} with {secondary} orientation",
        primary_name="position",
        tags=("base",),
    ),
    _spec(
        "performance-pose-base",
        "pose",
        "performance",
        "relaxed standing pose|balanced seated pose|walking pose|leaning pose|"
        "three-quarter standing pose|contrapposto pose|kneeling pose|crouched pose",
        "motion",
        "{primary} with {secondary}",
        primary_name="pose",
        tags=("base",),
    ),
    _spec(
        "performance-hand-pose-base",
        "hand-pose",
        "performance",
        "hands resting naturally|one hand at the waist|hands loosely clasped|"
        "one hand touching the collar|hands in pockets|one hand holding an object|"
        "arms loosely folded|one hand supporting the chin",
        "motion",
        "{primary}, expressed through {secondary}",
        primary_name="gesture",
        tags=("base",),
    ),
    _spec(
        "performance-action-base",
        "action",
        "performance",
        "standing still|walking forward|turning toward camera|adjusting clothing|"
        "reading quietly|working at a table|looking through a window|pausing mid-conversation",
        "motion",
        "{primary} with {secondary}",
        primary_name="action",
        tags=("base",),
    ),
    _spec(
        "scene-location-studio",
        "location",
        "scene",
        "neutral portrait studio|daylight studio|industrial studio|white cyc studio|"
        "textured backdrop studio|compact home studio|large fashion studio|black box studio",
        "spatial",
        "a {primary} with {secondary}",
        primary_name="setting",
        priority=10,
        tags=("base", "studio", "indoor"),
    ),
    _spec(
        "scene-location-urban",
        "location",
        "scene",
        "quiet city street|busy pedestrian crossing|modern transit platform|"
        "brick-lined side street|rooftop terrace|public plaza|covered arcade|"
        "contemporary office district",
        "spatial",
        "a {primary} with {secondary}",
        primary_name="setting",
        priority=20,
        tags=("urban", "outdoor"),
    ),
    _spec(
        "scene-location-nature",
        "location",
        "scene",
        "woodland clearing|rocky shoreline|open grassland|mountain overlook|"
        "desert plateau|lakeside path|botanical garden|windswept dune",
        "spatial",
        "a {primary} with {secondary}",
        primary_name="setting",
        priority=30,
        tags=("nature", "outdoor"),
    ),
    _spec(
        "scene-location-interior",
        "location",
        "scene",
        "modern apartment|quiet library|independent cafe|art gallery|workshop interior|"
        "hotel lobby|conservatory|minimal office",
        "spatial",
        "a {primary} with {secondary}",
        primary_name="setting",
        priority=40,
        tags=("interior", "indoor"),
    ),
    _spec(
        "scene-location-historical",
        "location",
        "scene",
        "stone manor hall|timber-framed market street|formal period salon|"
        "historic railway platform|old university courtyard|rural stone cottage|"
        "classical colonnade|art-deco hotel interior",
        "era",
        "a {primary} with {secondary}",
        primary_name="setting",
        priority=50,
        tags=("historical",),
    ),
    _spec(
        "scene-location-fantasy",
        "location",
        "scene",
        "moonlit observatory|floating garden terrace|ancient woodland sanctuary|"
        "crystal archive|desert sky temple|mist-covered citadel|subterranean library|"
        "celestial navigation chamber",
        "spatial",
        "a {primary} with {secondary}",
        primary_name="setting",
        priority=60,
        tags=("fantasy",),
    ),
    _spec(
        "scene-location-dark",
        "location",
        "scene",
        "abandoned manor corridor|fog-covered cemetery path|weathered stone chapel|"
        "empty midnight theater|shadowed forest trail|decaying conservatory|"
        "silent underground station|storm-darkened coastal house",
        "atmospheric",
        "a non-graphic {primary} with {secondary}",
        primary_name="setting",
        safety="dark-atmospheric",
        priority=70,
        tags=("dark", "gothic"),
    ),
    _spec(
        "scene-background-base",
        "background",
        "scene",
        "plain tonal background|soft gradient background|textured plaster background|"
        "distant architectural background|layered natural background|windowed background|"
        "graphic color-block background|deep shadow background",
        "spatial",
        "a {primary} arranged with {secondary}",
        primary_name="background",
        tags=("base",),
    ),
    _spec(
        "scene-architecture-base",
        "architecture",
        "scene",
        "modernist concrete|warm timber|industrial brick|classical stone|art-deco geometry|"
        "vernacular plaster|glass-and-steel|weathered masonry",
        "spatial",
        "{primary} architecture with {secondary}",
        primary_name="material-language",
        tags=("base",),
    ),
    _spec(
        "scene-set-dressing-base",
        "set-dressing",
        "scene",
        "minimal furniture|books and papers|studio equipment|potted plants|"
        "ceramic objects|textile layers|workshop tools|framed artwork",
        "spatial",
        "{primary} organized through {secondary}",
        primary_name="prop-family",
        tags=("base",),
    ),
    _spec(
        "scene-time-of-day-base",
        "time-of-day",
        "scene",
        "pre-dawn|sunrise|early morning|late morning|midday|late afternoon|sunset|night",
        "light",
        "{primary} timing with {secondary}",
        primary_name="period",
        tags=("base",),
    ),
    _spec(
        "scene-season-base",
        "season",
        "scene",
        "early spring|late spring|early summer|late summer|early autumn|late autumn|"
        "early winter|late winter",
        "atmospheric",
        "{primary} seasonal character with {secondary}",
        primary_name="seasonal-period",
        tags=("base",),
    ),
    _spec(
        "scene-weather-base",
        "weather",
        "scene",
        "clear weather|light cloud cover|overcast weather|light rain|steady rain|"
        "light snowfall|dry wind|humid calm",
        "atmospheric",
        "{primary} with {secondary}",
        primary_name="condition",
        tags=("base",),
    ),
    _spec(
        "scene-atmosphere-base",
        "atmosphere",
        "scene",
        "quiet atmosphere|lively atmosphere|contemplative atmosphere|formal atmosphere|"
        "intimate atmosphere|expansive atmosphere|mysterious atmosphere|optimistic atmosphere",
        "atmospheric",
        "{primary} carried by {secondary}",
        primary_name="mood",
        tags=("base",),
    ),
    _spec(
        "cinematography-lighting-setup-base",
        "lighting-setup",
        "cinematography",
        "single-key setup|key-and-fill setup|three-point setup|window-key setup|"
        "large-source wrap setup|hard-key setup|rim-accent setup|top-light setup",
        "light",
        "{primary} with {secondary}",
        primary_name="setup",
        tags=("base",),
    ),
    _spec(
        "cinematography-light-source-base",
        "light-source",
        "cinematography",
        "north-facing window light|direct sunlight|open-shade daylight|large softbox|"
        "beauty dish|fresnel lamp|practical room light|reflected bounce light",
        "light",
        "{primary} shaped with {secondary}",
        primary_name="source",
        tags=("base",),
    ),
    _spec(
        "cinematography-light-direction-base",
        "light-direction",
        "cinematography",
        "front light|three-quarter light|side light|back light|top light|under light|"
        "cross light|edge light",
        "light",
        "{primary} with {secondary}",
        primary_name="direction",
        tags=("base",),
    ),
    _spec(
        "cinematography-light-quality-base",
        "light-quality",
        "cinematography",
        "very soft light|soft light|moderately soft light|neutral light|moderately hard light|"
        "hard light|diffused light|specular light",
        "light",
        "{primary} producing {secondary}",
        primary_name="quality",
        tags=("base",),
    ),
    _spec(
        "cinematography-light-temperature-base",
        "light-temperature",
        "cinematography",
        "cool blue light|cool-neutral light|neutral white light|warm-neutral light|"
        "warm amber light|mixed warm-cool light|daylight-balanced light|tungsten-balanced light",
        "color",
        "{primary} with {secondary}",
        primary_name="temperature",
        tags=("base",),
    ),
    _spec(
        "cinematography-shot-size-base",
        "shot-size",
        "cinematography",
        "extreme close-up|close-up|head-and-shoulders shot|bust shot|waist-up shot|"
        "three-quarter shot|full-body shot|environmental long shot",
        "camera",
        "{primary} with {secondary}",
        primary_name="framing",
        tags=("base",),
    ),
    _spec(
        "cinematography-camera-angle-base",
        "camera-angle",
        "cinematography",
        "eye-level angle|slightly high angle|high angle|slightly low angle|low angle|"
        "profile angle|over-shoulder angle|overhead angle",
        "camera",
        "{primary} carrying {secondary}",
        primary_name="angle",
        tags=("base",),
    ),
    _spec(
        "cinematography-lens-focal-base",
        "lens-focal",
        "cinematography",
        "24mm wide lens|35mm environmental lens|40mm natural-wide lens|50mm normal lens|"
        "65mm short portrait lens|85mm portrait lens|105mm portrait lens|135mm compressed lens",
        "camera",
        "{primary} used with {secondary}",
        primary_name="focal-family",
        tags=("base",),
    ),
    _spec(
        "cinematography-aperture-base",
        "aperture",
        "cinematography",
        "f-1-4 aperture|f-2 aperture|f-2-8 aperture|f-4 aperture|f-5-6 aperture|"
        "f-8 aperture|f-11 aperture|variable aperture strategy",
        "camera",
        "{primary} chosen for {secondary}",
        primary_name="aperture-setting",
        tags=("base",),
    ),
    _spec(
        "cinematography-focus-base",
        "focus",
        "cinematography",
        "eye-priority focus|face-priority focus|shallow selective focus|moderate depth focus|"
        "deep scene focus|foreground-to-subject focus|split-plane focus|soft-edge focus",
        "camera",
        "{primary} with {secondary}",
        primary_name="focus-strategy",
        tags=("base",),
    ),
    _spec(
        "cinematography-camera-motion-base",
        "camera-motion",
        "cinematography",
        "locked camera|gentle handheld camera|slow push-in|slow pull-back|lateral tracking|"
        "subtle orbit|measured tilt|measured pan",
        "motion",
        "{primary} carrying {secondary}",
        primary_name="motion-strategy",
        tags=("base",),
    ),
    _spec(
        "cinematography-composition-base",
        "composition",
        "cinematography",
        "centered composition|rule-of-thirds composition|balanced asymmetry|"
        "strong negative space|layered foreground composition|frame-within-frame composition|"
        "diagonal composition|formal symmetry",
        "camera",
        "{primary} with {secondary}",
        primary_name="structure",
        tags=("base",),
    ),
    _spec(
        "cinematography-exposure-film-look-base",
        "exposure-film-look",
        "cinematography",
        "clean digital exposure|gentle highlight rolloff|protected highlights|open shadows|"
        "low-key exposure|high-key exposure|fine-grain film response|soft negative-film response",
        "finish",
        "{primary} with a {secondary}",
        primary_name="response",
        tags=("base",),
    ),
    _spec(
        "style-photo-genre-base",
        "photo-genre",
        "style",
        "contemporary portrait|professional headshot|editorial fashion|lifestyle portrait|"
        "street portrait|studio beauty|documentary portrait|cinematic portrait",
        "camera",
        "{primary} direction with {secondary}",
        primary_name="genre",
        priority=10,
        tags=("base", "photographic"),
    ),
    _spec(
        "style-photo-genre-art",
        "photo-genre",
        "style",
        "fine-art portrait|conceptual portrait|monochrome portrait|historical portrait|"
        "fantasy portrait|dark atmospheric portrait|environmental portrait|full-body fashion",
        "camera",
        "{primary} direction with {secondary}",
        primary_name="genre",
        priority=20,
        tags=("art-direction",),
    ),
    _spec(
        "style-visual-medium-base",
        "visual-medium",
        "style",
        "natural digital photograph|fine-grain film photograph|large-format photograph|"
        "instant-film photograph|black-and-white photograph|hand-colored photograph|"
        "editorial print photograph|cinematic still",
        "finish",
        "{primary} with a {secondary}",
        primary_name="medium",
        tags=("base",),
    ),
    _spec(
        "style-visual-era-base",
        "visual-era",
        "style",
        "contemporary visual language|late twentieth-century visual language|"
        "mid-century visual language|art-deco visual language|victorian visual language|"
        "renaissance-inspired visual language|timeless visual language|near-future visual language",
        "era",
        "{primary} with {secondary}",
        primary_name="era",
        tags=("base",),
    ),
    _spec(
        "style-color-grading-base",
        "color-grading",
        "style",
        "neutral grade|warm skin-focused grade|cool architectural grade|muted editorial grade|"
        "rich cinematic grade|pastel fashion grade|monochrome tonal grade|split warm-cool grade",
        "color",
        "{primary} with {secondary}",
        primary_name="grade",
        tags=("base",),
    ),
    _spec(
        "style-finish-base",
        "finish",
        "style",
        "natural finish|clean commercial finish|soft editorial finish|textured filmic finish|"
        "matte print finish|glossy campaign finish|subtle archival finish|"
        "restrained cinematic finish",
        "finish",
        "{primary} with a {secondary}",
        primary_name="finish-family",
        tags=("base",),
    ),
    _spec(
        "style-quality-base",
        "quality",
        "style",
        "clear subject detail|natural skin detail|coherent fabric detail|controlled edge detail|"
        "clean tonal separation|stable anatomical detail|consistent perspective detail|"
        "artifact-free photographic detail",
        "finish",
        "{primary} with a {secondary}",
        primary_name="quality-target",
        tags=("base",),
    ),
    _spec(
        "negative-base",
        "negative-base",
        "negative",
        "low-resolution artifacts|compression artifacts|unintended text|unintended watermark|"
        "duplicate subject|cropped subject error|background tiling|random border artifacts",
        "negative",
        "{primary} at {secondary}",
        primary_name="artifact-family",
        tags=("base", "level-minimal"),
    ),
    _spec(
        "negative-anatomy",
        "negative-anatomy",
        "negative",
        "malformed hands|extra fingers|missing fingers|fused limbs|duplicated limbs|"
        "misaligned eyes|distorted facial structure|impossible joint direction",
        "negative",
        "{primary} at {secondary}",
        primary_name="artifact-family",
        tags=("anatomy", "level-standard"),
    ),
    _spec(
        "negative-camera",
        "negative-camera",
        "negative",
        "accidental motion blur|missed subject focus|extreme lens distortion|"
        "uncontrolled highlight clipping|crushed shadow detail|chromatic fringing|"
        "sensor-pattern artifacts|inconsistent depth of field",
        "negative",
        "{primary} at {secondary}",
        primary_name="artifact-family",
        tags=("camera", "level-standard"),
    ),
    _spec(
        "negative-context",
        "negative-context",
        "negative",
        "era-inconsistent objects|weather-inconsistent clothing|light-direction conflict|"
        "reflection inconsistency|scale inconsistency|floating accessories|"
        "background-subject intersection|unmotivated mixed lighting",
        "negative",
        "{primary} at {secondary}",
        primary_name="artifact-family",
        tags=("context", "level-strict"),
    ),
)


PROFILE_IDS: Final[tuple[str, ...]] = (
    "portrait-core",
    "professional-headshot",
    "virtual-model",
    "dataset-balanced",
    "editorial-fashion",
    "lifestyle",
    "street-portrait",
    "studio-beauty",
    "cinematic-portrait",
    "fine-art-portrait",
    "historical-portrait",
    "fantasy-portrait",
    "dark-fantasy-horror",
    "conceptual-portrait",
    "full-body-fashion",
)


def _slug(value: str) -> str:
    return _SLUG.sub("-", value.casefold()).strip("-")


def _facet_value(value: str) -> str:
    slug = _slug(value)
    return slug if slug[:1].isalpha() else f"value-{slug}"


def _special_tags(spec: PackSpec, primary_index: int, secondary_index: int) -> list[str]:
    tags = [spec.domain, spec.category, *spec.tags]
    if spec.library == "shot-size":
        tags.append(
            "framing-close"
            if primary_index <= 2
            else "framing-wide"
            if primary_index >= 6
            else "framing-medium"
        )
    if spec.library == "hair-length":
        tags.append(
            "hair-short"
            if primary_index <= 1
            else "hair-medium"
            if primary_index == 2
            else "hair-long"
        )
    if spec.library == "outerwear":
        tags.append(
            "outerwear-warm"
            if primary_index in {0, 1, 3, 7}
            else "outerwear-protective"
            if primary_index in {4, 5}
            else "outerwear-light"
        )
    if spec.library == "pose":
        tags.append(
            "pose-standing"
            if primary_index in {0, 2, 4, 5}
            else "pose-seated"
            if primary_index == 1
            else "pose-low"
        )
    if spec.library == "action":
        tags.append("action-dynamic" if primary_index in {1, 2, 3} else "action-contained")
    if spec.library == "time-of-day":
        tags.append("time-night" if primary_index in {0, 7} else "time-daylight")
    if spec.library == "season":
        tags.append(
            "season-cold"
            if primary_index >= 6
            else "season-hot"
            if primary_index in {2, 3}
            else "season-mild"
        )
    if spec.library == "weather":
        tags.append(
            "weather-cold"
            if primary_index == 5
            else "weather-wet"
            if primary_index in {3, 4}
            else "weather-dry"
        )
    if spec.library == "light-source":
        tags.append("source-daylight" if primary_index <= 2 else "source-artificial")
    if spec.library == "camera-motion":
        tags.append("motion-static" if primary_index == 0 else "motion-dynamic")
    if spec.library == "visual-era":
        tags.append("era-modern" if primary_index in {0, 1, 6, 7} else "era-historical")
    if spec.library == "wardrobe-theme":
        tags.append(
            "era-historical"
            if "historical" in spec.tags
            else "era-fantasy"
            if "fantasy" in spec.tags
            else "era-modern"
        )
    if secondary_index >= 6:
        tags.append("rarity-rare")
    elif secondary_index >= 4:
        tags.append("rarity-uncommon")
    else:
        tags.append("rarity-common")
    return sorted(set(tags))


def _rules(spec: PackSpec, primary_index: int) -> dict[str, object]:
    rules: dict[str, object] = {}
    excludes: list[dict[str, object]] = []
    requires: list[dict[str, object]] = []
    prefer: list[dict[str, object]] = []
    if spec.library == "hair-style" and primary_index in {3, 4, 5, 6}:
        requires.append(
            {
                "field": "hair-length",
                "operator": "contains_tag",
                "value": "hair-long",
            }
        )
    if spec.library == "weather" and primary_index == 5:
        excludes.append({"field": "season", "operator": "contains_tag", "value": "season-hot"})
        prefer.append(
            {
                "field": "outerwear",
                "operator": "contains_tag",
                "value": "outerwear-warm",
                "multiplier": 1.8,
            }
        )
    elif spec.library == "weather" and primary_index in {3, 4}:
        prefer.append(
            {
                "field": "outerwear",
                "operator": "contains_tag",
                "value": "outerwear-protective",
                "multiplier": 1.6,
            }
        )
    elif spec.library == "light-source" and primary_index <= 2:
        excludes.append({"field": "time-of-day", "operator": "contains_tag", "value": "time-night"})
    elif spec.library == "camera-motion" and primary_index != 0:
        excludes.append(
            {"field": "shot-size", "operator": "contains_tag", "value": "framing-close"}
        )
    elif spec.library == "visual-era" and primary_index not in {0, 1, 6, 7}:
        excludes.append(
            {
                "field": "wardrobe-theme",
                "operator": "contains_tag",
                "value": "era-modern",
            }
        )
        prefer.append(
            {
                "field": "location",
                "operator": "contains_tag",
                "value": "historical",
                "multiplier": 1.8,
            }
        )
    if excludes:
        rules["excludes"] = excludes
    if requires:
        rules["requires"] = requires
    if prefer:
        rules["prefer"] = prefer
    return rules


def _option(spec: PackSpec, primary_index: int, secondary_index: int) -> dict[str, object]:
    primary = spec.primary[primary_index]
    secondary = SECONDARY[spec.secondary][secondary_index]
    phrase = spec.template.format(primary=primary, secondary=secondary)
    option_id = f"{spec.pack_id}-{_slug(primary)}-{_slug(secondary)}"
    weight = 1.0 if secondary_index < 4 else 0.7 if secondary_index < 6 else 0.4
    if spec.safety == "experimental":
        weight = 0.15
    if spec.domain == "negative":
        variants = [
            {"id": "plain", "text": phrase, "weight": 1.0},
            {"id": "avoid", "text": f"avoid {phrase}", "weight": 0.8},
            {"id": "exclude", "text": f"exclude {phrase}", "weight": 0.6},
        ]
    else:
        variants = [
            {"id": "plain", "text": phrase, "weight": 1.0},
            {"id": "observed", "text": f"showing {phrase}", "weight": 0.8},
            {"id": "rendered", "text": f"rendered with {phrase}", "weight": 0.6},
        ]
    option: dict[str, object] = {
        "id": option_id,
        "semantic_key": option_id,
        "text": phrase,
        "sentence": f"{phrase[:1].upper()}{phrase[1:]}.",
        "variants": variants,
        "weight": weight,
        "status": "active",
        "family": f"{spec.pack_id}-{_slug(primary)}",
        "tags": _special_tags(spec, primary_index, secondary_index),
        "facets": {
            spec.primary_name: _facet_value(primary),
            spec.secondary_name: _facet_value(secondary),
        },
        "subcategory": _facet_value(primary),
        "intensity": "subtle"
        if secondary_index < 2
        else "moderate"
        if secondary_index < 6
        else "strong",
        "safety": spec.safety,
        "join_hint": "sentence",
    }
    option.update(_rules(spec, primary_index))
    return option


def _pack(spec: PackSpec) -> dict[str, object]:
    options = [
        _option(spec, primary_index, secondary_index)
        for primary_index in range(8)
        for secondary_index in range(8)
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "id": spec.pack_id,
        "version": CATALOG_VERSION,
        "library": spec.library,
        "domain": spec.domain,
        "category": spec.category,
        "language": "en",
        "status": spec.status,
        "safety": spec.safety,
        "tags": sorted(set(spec.tags)),
        "fallback_option_id": _fallback_option(spec)["id"],
        "options": options,
    }


def _fallback_option(spec: PackSpec) -> dict[str, object]:
    primary_index = 3 if spec.library == "light-source" else 0
    return _option(spec, primary_index, 0)


def _profile_sections(profile_id: str) -> tuple[str, ...]:
    identity_core = (
        "subject-type",
        "adult-age",
        "face-shape",
        "eye-color",
        "skin-tone",
        "skin-texture",
        "hair-color",
        "hair-length",
        "hair-texture",
        "hair-style",
    )
    identity_detail = (
        "identity-archetype",
        "facial-structure",
        "eye-shape",
        "eyebrows",
        "nose",
        "mouth",
        "skin-details",
        "distinguishing-features",
    )
    wardrobe_core = ("wardrobe-theme", "tops", "outerwear", "palette")
    wardrobe_full = (
        "bottoms",
        "one-piece",
        "footwear",
        "materials",
        "patterns",
        "accessories",
        "jewelry",
        "headwear",
    )
    performance_core = ("expression", "gaze", "pose", "action")
    performance_detail = ("head-position", "hand-pose")
    scene_core = ("location", "time-of-day", "weather", "atmosphere")
    scene_detail = ("background", "architecture", "set-dressing", "season")
    camera_core = (
        "lighting-setup",
        "light-source",
        "light-quality",
        "shot-size",
        "camera-angle",
        "lens-focal",
        "focus",
        "composition",
    )
    camera_detail = (
        "light-direction",
        "light-temperature",
        "aperture",
        "camera-motion",
        "exposure-film-look",
    )
    style_core = ("photo-genre", "visual-medium", "color-grading", "quality")
    style_detail = ("visual-era", "finish")
    negative = ("negative-base", "negative-anatomy", "negative-camera", "negative-context")
    base = (
        *identity_core,
        *wardrobe_core,
        *performance_core,
        *scene_core,
        *camera_core,
        *style_core,
        *negative,
    )
    if profile_id == "dataset-balanced":
        return tuple(
            library
            for library in dict.fromkeys(spec.library for spec in SPECS)
            if library != "one-piece"
        )
    if profile_id == "professional-headshot":
        return (
            *identity_core,
            *identity_detail,
            "wardrobe-theme",
            "tops",
            "expression",
            "gaze",
            "head-position",
            "location",
            "background",
            *camera_core,
            *style_core,
            *negative,
        )
    if profile_id in {"editorial-fashion", "full-body-fashion", "virtual-model"}:
        result = (
            *identity_core,
            *identity_detail,
            "facial-hair",
            "body-build",
            *wardrobe_core,
            *wardrobe_full,
            *performance_core,
            *performance_detail,
            *scene_core,
            *scene_detail,
            *camera_core,
            *camera_detail,
            *style_core,
            *style_detail,
            *negative,
        )
        if profile_id in {"virtual-model", "full-body-fashion"}:
            return tuple(section for section in result if section not in {"tops", "bottoms"})
        return tuple(section for section in result if section != "one-piece")
    if profile_id == "studio-beauty":
        return (
            *identity_core,
            *identity_detail,
            "wardrobe-theme",
            "one-piece",
            "jewelry",
            "palette",
            *performance_core,
            "head-position",
            "location",
            "background",
            *camera_core,
            *camera_detail,
            *style_core,
            "finish",
            *negative,
        )
    if profile_id in {
        "cinematic-portrait",
        "fine-art-portrait",
        "historical-portrait",
        "fantasy-portrait",
        "dark-fantasy-horror",
        "conceptual-portrait",
    }:
        return (
            *identity_core,
            "identity-archetype",
            "facial-structure",
            "body-build",
            *wardrobe_core,
            "materials",
            "accessories",
            *performance_core,
            *scene_core,
            *scene_detail,
            *camera_core,
            *camera_detail,
            *style_core,
            *style_detail,
            *negative,
        )
    if profile_id in {"lifestyle", "street-portrait"}:
        return (
            *base,
            "body-build",
            "bottoms",
            "footwear",
            "hand-pose",
            "background",
            "set-dressing",
            "camera-motion",
            "finish",
        )
    return base


def _profile_pack_filter(profile_id: str, sections: tuple[str, ...]) -> tuple[str, ...]:
    by_library: dict[str, list[PackSpec]] = {}
    for spec in SPECS:
        by_library.setdefault(spec.library, []).append(spec)
    themed: dict[str, set[str]] = {
        "editorial-fashion": {"editorial", "fashion", "base", "contemporary"},
        "full-body-fashion": {"editorial", "fashion", "mature", "base", "contemporary"},
        "historical-portrait": {"historical", "base"},
        "fantasy-portrait": {"fantasy", "base"},
        "dark-fantasy-horror": {"dark", "gothic", "fantasy", "base"},
        "street-portrait": {"urban", "base", "contemporary"},
        "lifestyle": {"interior", "nature", "base", "contemporary"},
        "fine-art-portrait": {"art-direction", "nature", "studio", "base"},
        "conceptual-portrait": {"art-direction", "fantasy", "studio", "base"},
        "cinematic-portrait": {"art-direction", "urban", "interior", "base"},
    }
    focused: dict[str, dict[str, set[str]]] = {
        "historical-portrait": {
            "wardrobe-theme": {"historical"},
            "location": {"historical"},
        },
        "fantasy-portrait": {
            "wardrobe-theme": {"fantasy"},
            "location": {"fantasy"},
        },
        "dark-fantasy-horror": {
            "wardrobe-theme": {"dark"},
            "location": {"dark"},
        },
        "street-portrait": {"location": {"urban"}},
        "lifestyle": {"location": {"interior", "nature"}},
        "fine-art-portrait": {"location": {"studio", "nature"}},
        "conceptual-portrait": {"location": {"studio", "fantasy"}},
        "cinematic-portrait": {"location": {"urban", "interior"}},
        "editorial-fashion": {"wardrobe-theme": {"editorial"}},
        "full-body-fashion": {"wardrobe-theme": {"editorial"}},
    }
    wanted = themed.get(profile_id, {"base", "studio", "contemporary"})
    enabled: list[str] = []
    for library in sections:
        candidates = by_library[library]
        focused_tags = focused.get(profile_id, {}).get(library)
        if focused_tags is not None:
            matches = [spec for spec in candidates if focused_tags.intersection(spec.tags)]
        else:
            matches = [
                spec for spec in candidates if not spec.tags or wanted.intersection(spec.tags)
            ]
        if not matches:
            matches = [min(candidates, key=lambda spec: (spec.priority, spec.pack_id))]
        enabled.extend(spec.pack_id for spec in matches)
    return tuple(sorted(set(enabled)))


def _profile(profile_id: str, fallbacks: dict[str, str]) -> dict[str, object]:
    mode = (
        "dataset"
        if profile_id == "dataset-balanced"
        else "strict"
        if profile_id in {"professional-headshot", "historical-portrait"}
        else "creative"
        if profile_id in {"conceptual-portrait", "fantasy-portrait", "dark-fantasy-horror"}
        else "balanced"
    )
    negative_level = (
        "minimal"
        if profile_id == "portrait-core"
        else "strict"
        if profile_id
        in {
            "professional-headshot",
            "historical-portrait",
            "dataset-balanced",
            "dark-fantasy-horror",
        }
        else "standard"
    )
    allowed_negative = {
        "minimal": {"negative-base"},
        "standard": {"negative-base", "negative-anatomy", "negative-camera"},
        "strict": {
            "negative-base",
            "negative-anatomy",
            "negative-camera",
            "negative-context",
        },
    }[negative_level]
    sections = tuple(
        section
        for section in _profile_sections(profile_id)
        if not section.startswith("negative-") or section in allowed_negative
    )
    enabled_packs = _profile_pack_filter(profile_id, sections)
    enabled_pack_set = frozenset(enabled_packs)
    effective_fallbacks = {
        section: str(
            _fallback_option(
                next(
                    spec
                    for spec in SPECS
                    if spec.library == section and spec.pack_id in enabled_pack_set
                )
            )["id"]
        )
        for section in sections
    }
    negative_sections = [section for section in sections if section.startswith("negative-")]
    positive_sections = [section for section in sections if not section.startswith("negative-")]
    verbosity = (
        "compact"
        if profile_id == "professional-headshot"
        else "detailed"
        if mode == "creative"
        else "standard"
    )
    safety = ["general"]
    if profile_id in {"editorial-fashion", "full-body-fashion"}:
        safety.append("fashion-mature")
    if profile_id == "dark-fantasy-horror":
        safety.append("dark-atmospheric")
    section_data: dict[str, object] = {}
    for section in sections:
        mode_value = "random"
        section_data[section] = {
            "required": section not in negative_sections,
            "library": section,
            "mode": mode_value,
            "group": _group(section),
            "fallback": effective_fallbacks.get(section, fallbacks[section]),
        }
    positive_template = ". ".join(f"{{{section}}}" for section in positive_sections) + "."
    negative_template = ", ".join(f"{{{section}}}" for section in negative_sections) + "."
    return {
        "schema_version": SCHEMA_VERSION,
        "id": profile_id,
        "version": CATALOG_VERSION,
        "display_name": profile_id.replace("-", " ").title(),
        "language": "en",
        "catalog_version": CATALOG_VERSION,
        "enabled_packs": list(enabled_packs),
        "allowed_safety_classes": safety,
        "verbosity": verbosity,
        "negative_level": negative_level,
        "minimum_sections": 16,
        "minimum_prompt_characters": 180,
        "max_selection_attempts": 32,
        "section_order": list(sections),
        "sections": section_data,
        "templates": {"positive": positive_template, "negative": negative_template},
        "allow_empty_negative": False,
        "metadata": {
            "purpose": profile_id.replace("-", " "),
            "content_policy": "adults-only",
            "recommended_mode": mode,
            "seed_groups": sorted({_group(section) for section in sections}),
            "expected_prompt_size": verbosity,
            "density": "adaptive",
            "verbosity_omit": {
                "compact": [
                    "skin-details",
                    "distinguishing-features",
                    "patterns",
                    "set-dressing",
                    "camera-motion",
                    "exposure-film-look",
                ]
            },
            "adaptive_omissions": {
                "framing-close": [
                    "body-build",
                    "bottoms",
                    "footwear",
                    "pose",
                    "hand-pose",
                ]
            },
        },
    }


def _group(section: str) -> str:
    for group, values in {
        "identity": {
            "subject-type",
            "adult-age",
            "identity-archetype",
            "face-shape",
            "facial-structure",
            "eye-color",
            "eye-shape",
            "eyebrows",
            "nose",
            "mouth",
            "distinguishing-features",
        },
        "appearance": {
            "skin-tone",
            "skin-texture",
            "skin-details",
            "hair-color",
            "hair-length",
            "hair-texture",
            "hair-style",
            "facial-hair",
            "body-build",
        },
        "wardrobe": {
            "wardrobe-theme",
            "tops",
            "bottoms",
            "one-piece",
            "outerwear",
            "footwear",
            "materials",
            "patterns",
            "accessories",
            "jewelry",
            "headwear",
            "palette",
        },
        "performance": {
            "expression",
            "gaze",
            "head-position",
            "pose",
            "hand-pose",
            "action",
        },
        "scene": {
            "location",
            "background",
            "architecture",
            "set-dressing",
            "time-of-day",
            "season",
            "weather",
            "atmosphere",
        },
        "lighting": {
            "lighting-setup",
            "light-source",
            "light-direction",
            "light-quality",
            "light-temperature",
        },
        "camera": {
            "shot-size",
            "camera-angle",
            "lens-focal",
            "aperture",
            "focus",
            "camera-motion",
            "composition",
            "exposure-film-look",
        },
        "style": {
            "photo-genre",
            "visual-medium",
            "visual-era",
            "color-grading",
            "finish",
            "quality",
        },
    }.items():
        if section in values:
            return group
    return "negative"


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    """Generate packs, index, and all official profile files deterministically."""
    packs = [_pack(spec) for spec in SPECS]
    libraries: dict[str, dict[str, object]] = {}
    fallbacks: dict[str, str] = {}
    references: list[dict[str, object]] = []
    for spec, pack in zip(SPECS, packs, strict=True):
        relative_path = Path("packs") / spec.domain / f"{spec.pack_id}.json"
        _write_json(_CATALOG_ROOT / relative_path, pack)
        references.append(
            {
                "id": spec.pack_id,
                "library": spec.library,
                "domain": spec.domain,
                "path": relative_path.as_posix(),
                "version": CATALOG_VERSION,
                "language": "en",
                "status": spec.status,
                "safety": spec.safety,
                "tags": sorted(set(spec.tags)),
                "dependencies": [],
                "priority": spec.priority,
            }
        )
        logical = libraries.setdefault(
            spec.library,
            {
                "display_name": spec.library.replace("-", " ").title(),
                "packs": [],
                "fallback_option_id": pack["fallback_option_id"],
            },
        )
        logical["packs"].append(spec.pack_id)  # type: ignore[union-attr]
        fallbacks.setdefault(spec.library, str(pack["fallback_option_id"]))
    for logical in libraries.values():
        logical["packs"] = sorted(logical["packs"])  # type: ignore[arg-type]
    index = {
        "schema_version": SCHEMA_VERSION,
        "id": "prompt-architect-catalog",
        "version": CATALOG_VERSION,
        "language": "en",
        "packs": sorted(references, key=lambda item: (item["priority"], item["id"])),
        "libraries": dict(sorted(libraries.items())),
    }
    _write_json(_CATALOG_ROOT / "index.json", index)
    for profile_id in (*PROFILE_IDS, "dataset", "portrait"):
        (_PROFILE_ROOT / f"{profile_id}.json").unlink(missing_ok=True)
    for profile_id in PROFILE_IDS:
        _write_json(_PROFILE_ROOT / f"{profile_id}.json", _profile(profile_id, fallbacks))
    option_count = sum(len(pack["options"]) for pack in packs)  # type: ignore[arg-type]
    variant_count = option_count * 3
    print(
        f"PASS: {len(packs)} packs, {len(libraries)} logical libraries, "
        f"{option_count} options, {variant_count} variants, {len(PROFILE_IDS)} profiles"
    )


if __name__ == "__main__":
    main()
