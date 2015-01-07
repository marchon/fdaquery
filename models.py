from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.engine.url import URL


Base = declarative_base()

patient_drugs = Table('patient_drugs', Base.metadata,
    Column('patientID', Integer, ForeignKey('patient.id')),
    Column('drugID', Integer, ForeignKey('drugs.id'))
)

patient_reaction = Table('patient_reaction', Base.metadata,
    Column('patientID', Integer, ForeignKey('patient.id')),
    Column('reactionID', Integer, ForeignKey('reaction.id'))
)


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    patientID = Column(Integer, ForeignKey('patient.id'))
    senderID = Column(Integer, ForeignKey('sender.id'))
    receiverID = Column(Integer, ForeignKey('receiver.id'))
    epoch = Column(String)
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
    primarycountry = Column(String)
    primarysource_qualification = Column(String)
    primarysource_reportercountry = Column(String)
    reportduplicate_duplicatesource = Column(String)
    reportduplicate_duplicatenumb = Column(String)

    patient = relationship("Patient", backref="events")
    sender = relationship("Sender", backref="events")
    receiver = relationship("Receiver", backref="events")


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
    openfdaID = Column(Integer, ForeignKey('openfda.id'))
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
    drugstructureunitnumb = Column(String)
    drugadministrationroute = Column(String)
    drugauthorizationnumb = Column(String)
    drugbatchnumb = Column(String)
    drugcharacterization = Column(String)
    drugdosagetext = Column(String)
    drugenddate = Column(String)
    drugenddateformat = Column(String)
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


