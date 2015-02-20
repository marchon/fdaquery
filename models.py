from sqlalchemy import Column, Float, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.engine.url import URL


Base = declarative_base()

patient_drugs = Table('patient_drugs', Base.metadata,
    Column('patientid', Integer, ForeignKey('patient.id')),
    Column('drugid', Integer, ForeignKey('drugs.id'))
)

patient_reaction = Table('patient_reaction', Base.metadata,
    Column('patientid', Integer, ForeignKey('patient.id')),
    Column('reactionid', Integer, ForeignKey('reaction.id'))
)


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    patientid = Column(Integer, ForeignKey('patient.id'))
    senderid = Column(Integer, ForeignKey('sender.id'))
    receiverid = Column(Integer, ForeignKey('receiver.id'))
    primarysourceid = Column(Integer, ForeignKey('primarysource.id'))
    reportduplicateid = Column(Integer, ForeignKey('reportduplicate.id'))
    epoch = Column(Float)
    companynumb = Column(String)
    fulfillexpeditecriteria = Column(String)
    receiptdate = Column(String)
    receiptdateformat = Column(String)
    receivedate = Column(String)
    receivedateformat = Column(String)
    safetyreportid = Column(String)
    safetyreportversion = Column(String)
    serious = Column(String)
    seriousnesscongenitalanomali = Column(String)
    seriousnessdeath = Column(String)
    seriousnessdisabling = Column(String)
    seriousnesshospitalization = Column(String)
    seriousnesslifethreatening = Column(String)
    seriousnessother = Column(String)
    transmissiondate = Column(String)
    transmissiondateformat = Column(String)
    duplicate = Column(String)
    occurcountry = Column(String)
    primarysourcecountry = Column(String)
    primarysource_qualification = Column(String)
    primarysource_reportercountry = Column(String)
    reportduplicate_duplicatesource = Column(String)
    reportduplicate_duplicatenumb = Column(String)
    reporttype = Column(String)

    patient = relationship("Patient", backref="events")
    sender = relationship("Sender", backref="events")
    receiver = relationship("Receiver", backref="events")
    primarysource = relationship("Primarysource", backref="events")
    reportduplicate = relationship("Reportduplicate", backref="events")


class Sender(Base):
    __tablename__ = 'sender'

    id = Column(Integer, primary_key=True)
    senderorganization = Column(String)
    sendertype = Column(String)


class Receiver(Base):
    __tablename__ = 'receiver'

    id = Column(Integer, primary_key=True)
    receiverorganization = Column(String)
    receivertype = Column(String)


class Primarysource(Base):
    __tablename__ = 'primarysource'

    id = Column(Integer, primary_key=True)
    qualification = Column(String)
    reportercountry = Column(String)


class Reportduplicate(Base):
    __tablename__ = 'reportduplicate'

    id = Column(Integer, primary_key=True)
    duplicatesource = Column(String)
    duplicatenumb = Column(String)


class Patient(Base):
    __tablename__ = 'patient'

    id = Column(Integer, primary_key=True)
    patientonsetage = Column(String)
    patientonsetageunit = Column(String)
    patientsex = Column(String)
    patientweight = Column(String)
    patientdeathdate = Column(String)
    patientdeathdateformat = Column(String)

    drugs = relationship("Drugs", secondary=patient_drugs, backref="patients")
    reaction = relationship("Reaction", secondary=patient_reaction, backref="patients")


class Reaction(Base):
    __tablename__ = 'reaction'

    id = Column(Integer, primary_key=True)
    reactionmeddrapt = Column(String)
    reactionmeddraversionpt = Column(String)
    reactionoutcome = Column(String)


class Drugs(Base):
    __tablename__ = 'drugs'

    id = Column(Integer, primary_key=True)
    openfdaid = Column(Integer, ForeignKey('openfda.id'))
    actiondrug = Column(String)
    drugadditional = Column(String)
    drugcumulativedosagenumb = Column(String)
    drugcumulativedosageunit = Column(String)
    drugdosageform = Column(String)
    drugintervaldosagedefinition = Column(String)
    drugintervaldosageunitnumb = Column(String)
    drugrecurreadministration = Column(String)
    drugseparatedosagenumb = Column(String)
    drugstructuredosagenumb = Column(String)
    drugstructuredosageunit = Column(String)
    drugadministrationroute = Column(String)
    drugauthorizationnumb = Column(String)
    drugbatchnumb = Column(String)
    drugcharacterization = Column(String)
    drugdosagetext = Column(String)
    drugindication = Column(String)
    drugenddate = Column(String)
    drugenddateformat = Column(String)
    drugstartdate = Column(String)
    drugstartdateformat = Column(String)
    drugtreatmentduration = Column(String)
    drugtreatmentdurationunit = Column(String)
    medicinalproduct = Column(String)

    openfda = relationship("Openfda", backref="drugs")


class Openfda(Base):
    __tablename__ = 'openfda'

    id = Column(Integer, primary_key=True)
    application_number = Column(String)
    brand_name = Column(String)
    generic_name = Column(String)
    manufacturer_name = Column(String)
    nui = Column(String)
    package_ndc = Column(String)
    pharm_class_cs = Column(String)
    pharm_class_epc = Column(String)
    pharm_class_moa = Column(String)
    product_ndc = Column(String)
    product_type = Column(String)
    route = Column(String)
    rxcui = Column(String)
    spl_id = Column(String)
    spl_set_id = Column(String)
    substance_name = Column(String)
    unii = Column(String)


class Event_json(Base):
    __tablename__ = 'event_json'

    id = Column(Integer, primary_key=True)
    event = Column(JSON)


class Meta(Base):
    __tablename__ = 'meta'

    id = Column(Integer, primary_key=True)
    last_updated = Column(String)
    limit = Column(String)
    total = Column(String)

