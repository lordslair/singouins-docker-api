# Collection: auction


.
├── _id (UUIDField)
├── created (DateTimeField)
├── item
│   ├── id (UUIDField)
│   ├── metaid (UUIDField)
│   ├── metatype (StringField)
│   └── rarity (StringField)
├── price (IntField)
├── seller
│   ├── id (UUIDField)
│   └── name (StringField)
└── updated (DateTimeField)