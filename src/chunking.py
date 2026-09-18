""" Text Chunking"""

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    # validate arguments
    if chunk_size <= 0:
        raise ValueError("Chunk size cannot be -ve")
    if overlap < 0:
        raise ValueError("Overlap cannot be -ve")
    if overlap >= chunk_size:
        raise ValueError("Overlap cannot be grater than chunk_size")        
    # make empty list called chunks
    chunks = []
    # set position to 0
    position = 0
    # while there is still text left:
    while len(text)-position > overlap:
        #slice a chunk from position
        chunk = text[position:position+chunk_size]
        #append chunk to chunks
        chunks.append(chunk)
        #move position forward
        position = position + chunk_size - overlap  
    # return chunks
    return chunks