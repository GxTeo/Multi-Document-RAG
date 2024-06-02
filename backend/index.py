from utils import *


from llama_index.core import (
    Settings,
    VectorStoreIndex, SimpleDirectoryReader, StorageContext
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.tools import QueryEngineTool, ToolMetadata

class QueryEngineTools:
    def __init__(self, collection_name, embed_model,  mongo_reader, mongo_client, chroma_client, db_name='Documents', top_k=3):
        self.top_k = top_k
        self.mongo_reader = mongo_reader
        self.mongo_client = mongo_client
        self.chroma_client = chroma_client
        self.db_name = db_name
        self.collection_name = collection_name
        Settings.embed_model = embed_model

    def __read_collection(self):
        docs_dict = {}
        field_names = ['text']

        collection = self.mongo_client[self.db_name][self.collection_name]
        for document in collection.find():
            query_dict = {'filename': document['filename']}
            doc = self.mongo_reader.load_data(db_name=self.db_name, collection_name=self.collection_name, query_dict=query_dict, field_names=field_names)
            doc[0].metadata['filename'] = document['filename']

            docs_dict[f"{document['filename']}"] = doc

        return docs_dict    
    
    def get_query_engine_tools(self):
        # lazy import

        query_engine_tools = []
        docs_dict = self.__read_collection()
        for filename, doc in docs_dict.items():
            filename = modify_string(filename)
            chroma_collection = self.chroma_client.get_or_create_collection(filename)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                doc, storage_context=storage_context
            )
            query_engine = index.as_query_engine(response_mode="tree_summarize", similarity_top_k=self.top_k)
            
            modify_filename = re.sub(r'\W+', '', filename)
            tool_name = modify_filename
            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=tool_name,
                    description=f"Query engine for {filename}"
                                 "Use a detailed plain text question as input to the tool",
                ),
            )
            query_engine_tools.append(tool)

        return query_engine_tools



 

