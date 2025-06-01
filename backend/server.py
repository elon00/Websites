from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import re


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Bible Models
class Verse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    book: str
    chapter: int
    verse: int
    text: Dict[str, str]  # {"english": "text", "hindi": "text", "hebrew": "text", "greek": "text"}
    transliteration: Dict[str, str] = {}  # {"hebrew": "transliterated text", "greek": "transliterated text"}
    cross_references: List[str] = []  # ["book chapter:verse", ...]
    notes: Dict[str, str] = {}  # {"commentary": "text", "study_notes": "text"}

class Book(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Dict[str, str]  # {"english": "Genesis", "hindi": "उत्पत्ति", ...}
    testament: str  # "old" or "new"
    chapters: int

class SearchResult(BaseModel):
    verses: List[Verse]
    total_count: int

# Sample Bible data
SAMPLE_BOOKS = [
    {
        "id": "gen",
        "name": {
            "english": "Genesis",
            "hindi": "उत्पत्ति",
            "hebrew": "בְּרֵאשִׁית",
            "greek": "Γένεσις"
        },
        "testament": "old",
        "chapters": 50
    },
    {
        "id": "joh",
        "name": {
            "english": "John",
            "hindi": "यूहन्ना",
            "hebrew": "יוחנן",
            "greek": "Ἰωάννης"
        },
        "testament": "new",
        "chapters": 21
    },
    {
        "id": "psa",
        "name": {
            "english": "Psalms",
            "hindi": "भजन संहिता",
            "hebrew": "תְּהִלִּים",
            "greek": "Ψαλμοί"
        },
        "testament": "old",
        "chapters": 150
    }
]

SAMPLE_VERSES = [
    {
        "id": "gen-1-1",
        "book": "Genesis",
        "chapter": 1,
        "verse": 1,
        "text": {
            "english": "In the beginning God created the heavens and the earth.",
            "hindi": "आदि में परमेश्वर ने आकाश और पृथ्वी की सृष्टि की।",
            "hebrew": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
            "greek": "Ἐν ἀρχῇ ἐποίησεν ὁ θεὸς τὸν οὐρανὸν καὶ τὴν γῆν"
        },
        "transliteration": {
            "hebrew": "B'reishit bara Elohim et hashamayim v'et ha'aretz",
            "greek": "En archē epoiēsen ho theos ton ouranon kai tēn gēn"
        },
        "cross_references": ["John 1:1", "Hebrews 11:3", "Psalms 33:6"],
        "notes": {
            "commentary": "The opening verse establishes God as the Creator of all things.",
            "study_notes": "The Hebrew word 'bara' specifically means to create ex nihilo (out of nothing)."
        }
    },
    {
        "id": "joh-1-1",
        "book": "John",
        "chapter": 1,
        "verse": 1,
        "text": {
            "english": "In the beginning was the Word, and the Word was with God, and the Word was God.",
            "hindi": "आदि में वचन था, और वचन परमेश्वर के साथ था, और वचन परमेश्वर था।",
            "hebrew": "בְּרֵאשִׁית הָיָה הַדָּבָר וְהַדָּבָר הָיָה אֶת הָאֱלֹהִים וֵאלֹהִים הָיָה הַדָּבָר",
            "greek": "Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος"
        },
        "transliteration": {
            "hebrew": "B'reishit hayah hadavar v'hadavar hayah et ha'Elohim vElohim hayah hadavar",
            "greek": "En archē ēn ho logos, kai ho logos ēn pros ton theon, kai theos ēn ho logos"
        },
        "cross_references": ["Genesis 1:1", "1 John 1:1", "Revelation 19:13"],
        "notes": {
            "commentary": "John begins his Gospel with the divine nature of Christ as the eternal Word.",
            "study_notes": "The Greek 'Logos' refers to the divine reason and creative word of God."
        }
    },
    {
        "id": "psa-23-1",
        "book": "Psalms",
        "chapter": 23,
        "verse": 1,
        "text": {
            "english": "The Lord is my shepherd; I shall not want.",
            "hindi": "यहोवा मेरा चरवाहा है; मुझे कुछ घटी न होगी।",
            "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
            "greek": "Κύριος ποιμαίνει με καὶ οὐδέν με ὑστερήσει"
        },
        "transliteration": {
            "hebrew": "Adonai ro'i lo echsar",
            "greek": "Kyrios poimainei me kai ouden me hysterēsei"
        },
        "cross_references": ["John 10:11", "Ezekiel 34:12", "Isaiah 40:11"],
        "notes": {
            "commentary": "This beloved psalm depicts God's care and provision for His people.",
            "study_notes": "The imagery of God as shepherd was common in ancient Near Eastern cultures."
        }
    },
    {
        "id": "gen-1-2",
        "book": "Genesis",
        "chapter": 1,
        "verse": 2,
        "text": {
            "english": "The earth was without form and void, and darkness was over the face of the deep. And the Spirit of God was hovering over the face of the waters.",
            "hindi": "पृथ्वी बेडौल और सुनसान पड़ी थी; और गहरे जल के ऊपर अन्धियारा था: तथा परमेश्वर का आत्मा जल के ऊपर मण्डराता था।",
            "hebrew": "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל־פְּנֵי הַמָּיִם",
            "greek": "ἡ δὲ γῆ ἦν ἀόρατος καὶ ἀκατασκεύαστος, καὶ σκότος ἐπάνω τῆς ἀβύσσου, καὶ πνεῦμα θεοῦ ἐπεφέρετο ἐπάνω τοῦ ὕδατος"
        },
        "transliteration": {
            "hebrew": "V'ha'aretz haytah tohu vavohu v'choshech al-p'nei t'hom v'ruach Elohim m'rachefet al-p'nei hamayim",
            "greek": "hē de gē ēn aoratos kai akataskeuastos, kai skotos epanō tēs abyssou, kai pneuma theou epephereto epanō tou hydatos"
        },
        "cross_references": ["Jeremiah 4:23", "2 Corinthians 4:6", "Genesis 8:1"],
        "notes": {
            "commentary": "The earth's initial state before God's creative work brought order and life.",
            "study_notes": "The Hebrew 'tohu vavohu' describes a state of chaos and emptiness."
        }
    }
]

# Initialize sample data on startup
@app.on_event("startup")
async def initialize_data():
    # Check if data already exists
    existing_books = await db.books.count_documents({})
    if existing_books == 0:
        # Insert sample books
        await db.books.insert_many(SAMPLE_BOOKS)
        logger.info("Sample books inserted")
    
    existing_verses = await db.verses.count_documents({})
    if existing_verses == 0:
        # Insert sample verses
        await db.verses.insert_many(SAMPLE_VERSES)
        logger.info("Sample verses inserted")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Bible API - Multilingual Bible with Cross-References"}

@api_router.get("/books", response_model=List[Dict[str, Any]])
async def get_books():
    """Get all Bible books"""
    books = await db.books.find({}, {"_id": 0}).to_list(100)
    return books

@api_router.get("/books/{book_name}/chapters/{chapter}", response_model=List[Verse])
async def get_chapter(book_name: str, chapter: int):
    """Get all verses from a specific chapter"""
    verses = await db.verses.find(
        {"book": book_name, "chapter": chapter}, 
        {"_id": 0}
    ).to_list(1000)
    return [Verse(**verse) for verse in verses]

@api_router.get("/verses/{verse_id}", response_model=Verse)
async def get_verse(verse_id: str):
    """Get a specific verse by ID"""
    verse = await db.verses.find_one({"id": verse_id}, {"_id": 0})
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    return Verse(**verse)

@api_router.get("/search", response_model=SearchResult)
async def search_verses(
    q: str = Query(..., description="Search query"),
    language: str = Query("english", description="Language to search in"),
    book: Optional[str] = Query(None, description="Filter by book"),
    testament: Optional[str] = Query(None, description="Filter by testament (old/new)"),
    limit: int = Query(20, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Search verses by text content"""
    # Build search query
    search_filter = {}
    
    # Text search using regex
    if language in ["english", "hindi", "hebrew", "greek"]:
        search_filter[f"text.{language}"] = {"$regex": q, "$options": "i"}
    
    # Book filter
    if book:
        search_filter["book"] = book
    
    # Testament filter (requires lookup to books collection)
    if testament:
        testament_books = await db.books.find(
            {"testament": testament}, 
            {"name.english": 1, "_id": 0}
        ).to_list(100)
        book_names = [book["name"]["english"] for book in testament_books]
        search_filter["book"] = {"$in": book_names}
    
    # Get total count
    total_count = await db.verses.count_documents(search_filter)
    
    # Get paginated results
    verses = await db.verses.find(
        search_filter, 
        {"_id": 0}
    ).skip(offset).limit(limit).to_list(limit)
    
    return SearchResult(
        verses=[Verse(**verse) for verse in verses],
        total_count=total_count
    )

@api_router.get("/cross-references/{verse_id}")
async def get_cross_references(verse_id: str):
    """Get cross-referenced verses for a given verse"""
    verse = await db.verses.find_one({"id": verse_id}, {"_id": 0})
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    cross_refs = verse.get("cross_references", [])
    referenced_verses = []
    
    for ref in cross_refs:
        # Parse reference format "Book Chapter:Verse"
        try:
            if ":" in ref:
                book_chapter, verse_num = ref.split(":")
                parts = book_chapter.rsplit(" ", 1)
                if len(parts) == 2:
                    ref_book = parts[0]
                    ref_chapter = int(parts[1])
                    ref_verse = int(verse_num)
                    
                    ref_verse_doc = await db.verses.find_one({
                        "book": ref_book,
                        "chapter": ref_chapter,
                        "verse": ref_verse
                    }, {"_id": 0})
                    
                    if ref_verse_doc:
                        referenced_verses.append(Verse(**ref_verse_doc))
        except (ValueError, IndexError):
            continue
    
    return {
        "original_verse": Verse(**verse),
        "cross_references": referenced_verses
    }

@api_router.get("/daily-verse", response_model=Verse)
async def get_daily_verse():
    """Get a daily verse (random verse for now)"""
    # For now, return a random verse - in production, this could be based on date
    pipeline = [{"$sample": {"size": 1}}]
    verses = await db.verses.aggregate(pipeline).to_list(1)
    if verses:
        verse = verses[0]
        verse.pop("_id", None)
        return Verse(**verse)
    else:
        # Fallback to first verse
        verse = await db.verses.find_one({}, {"_id": 0})
        return Verse(**verse)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
