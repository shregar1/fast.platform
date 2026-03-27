"""
HubSpot CRM client
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class HubSpotContact:
    """HubSpot contact"""
    id: str
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    properties: Dict[str, Any] = None


@dataclass
class HubSpotDeal:
    """HubSpot deal"""
    id: str
    dealname: str
    amount: Optional[float] = None
    stage: Optional[str] = None
    pipeline: Optional[str] = None
    closedate: Optional[str] = None
    properties: Dict[str, Any] = None


class HubSpotClient:
    """
    HubSpot CRM client
    """
    
    def __init__(self, api_key: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key
        self.access_token = access_token
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from hubspot import HubSpot
                
                if self.access_token:
                    self._client = HubSpot(access_token=self.access_token)
                else:
                    self._client = HubSpot(api_key=self.api_key)
                    
            except ImportError:
                raise ImportError("hubspot-api-client required for HubSpotClient")
        
        return self._client
    
    async def create_contact(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> HubSpotContact:
        """Create a contact"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        properties_dict = {"email": email}
        if firstname:
            properties_dict["firstname"] = firstname
        if lastname:
            properties_dict["lastname"] = lastname
        if properties:
            properties_dict.update(properties)
        
        simple_public_object_input = {"properties": properties_dict}
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: client.crm.contacts.basic_api.create(
                    simple_public_object_input=simple_public_object_input
                )
            )
        
        return HubSpotContact(
            id=result.id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            properties=properties_dict
        )
    
    async def get_contact(self, contact_id: str) -> Optional[HubSpotContact]:
        """Get a contact by ID"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(
                    pool,
                    lambda: client.crm.contacts.basic_api.get_by_id(contact_id)
                )
            
            props = result.properties
            return HubSpotContact(
                id=result.id,
                email=props.get("email"),
                firstname=props.get("firstname"),
                lastname=props.get("lastname"),
                phone=props.get("phone"),
                company=props.get("company"),
                properties=props
            )
        except Exception:
            return None
    
    async def create_deal(
        self,
        dealname: str,
        amount: Optional[float] = None,
        stage: Optional[str] = None,
        pipeline: Optional[str] = None,
        contact_ids: Optional[List[str]] = None
    ) -> HubSpotDeal:
        """Create a deal"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        properties = {"dealname": dealname}
        if amount:
            properties["amount"] = str(amount)
        if stage:
            properties["dealstage"] = stage
        if pipeline:
            properties["pipeline"] = pipeline
        
        simple_public_object_input = {"properties": properties}
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: client.crm.deals.basic_api.create(
                    simple_public_object_input=simple_public_object_input
                )
            )
        
        # Associate with contacts
        if contact_ids:
            for contact_id in contact_ids:
                await self._associate_deal_contact(result.id, contact_id)
        
        return HubSpotDeal(
            id=result.id,
            dealname=dealname,
            amount=amount,
            stage=stage,
            pipeline=pipeline,
            properties=properties
        )
    
    async def _associate_deal_contact(self, deal_id: str, contact_id: str) -> None:
        """Associate a deal with a contact"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.crm.deals.associations_api.create(
                    deal_id=deal_id,
                    to_object_type="contacts",
                    to_object_id=contact_id,
                    association_type="deal_to_contact"
                )
            )
    
    async def search_contacts(self, query: str) -> List[HubSpotContact]:
        """Search contacts"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        search_request = {
            "query": query,
            "properties": ["email", "firstname", "lastname", "phone"]
        }
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            results = await loop.run_in_executor(
                pool,
                lambda: client.crm.contacts.search_api.do_search(
                    public_object_search_request=search_request
                )
            )
        
        return [
            HubSpotContact(
                id=r.id,
                email=r.properties.get("email"),
                firstname=r.properties.get("firstname"),
                lastname=r.properties.get("lastname"),
                phone=r.properties.get("phone"),
                properties=r.properties
            )
            for r in results.results
        ]
