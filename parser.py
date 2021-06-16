import re
import emoji
import neologdn
import MeCab

def clean_text(text):
    normalized_text = neologdn.normalize(text)
    text_without_url = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', normalized_text)
    text_without_emoji = ''.join(['' if c in emoji.UNICODE_EMOJI else c for c in text_without_url])
    tmp = re.sub(r'(\d)([,.])(\d+)', r'\1\3', text_without_emoji)
    text_replaced_number = re.sub(r'\d+', '0', tmp)
    tmp = re.sub(r'[!-/:-@[-`{-~]', r' ', text_replaced_number)
    text_removed_symbol = re.sub(u'[■-♯・]', ' ', tmp)
    text_lower = text_removed_symbol.lower()
    return text_lower

# ストップワードをなんとかする
select_part = ['名詞', '代名詞', '形状詞', '副詞', '動詞', '形容詞']
def parse(text):
    text_cleaned = clean_text(text)
    tagger = MeCab.Tagger('')
    tagger.parse('')
    node = tagger.parseToNode(text_cleaned).next
    
    terms = set()
    while node.next:
        term = node.surface
        part = node.feature.split(',')[0]
        
        if part in select_part:
            terms.add(term)
        
        node = node.next
    
    text_parsed = ' '.join(terms)
    return text_parsed