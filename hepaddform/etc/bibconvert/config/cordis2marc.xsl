<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="2.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns:marc="http://www.loc.gov/MARC21/slim" 
xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
xmlns:dc="http://purl.org/dc/elements/1.1/" 
xmlns:fn="http://cdsweb.cern.ch/bibformat/fn"
xmlns:oaf="http://www.openaire.eu/oaf"
exclude-result-prefixes="marc fn">

<xsl:namespace-alias 
	stylesheet-prefix="marc"
	result-prefix="#default" />
<xsl:namespace-alias 
	stylesheet-prefix="oai_dc"
	result-prefix="#default" />
<xsl:namespace-alias 
	stylesheet-prefix="dc"
	result-prefix="#default" />
<xsl:namespace-alias 
	stylesheet-prefix="xsi"
	result-prefix="#default" />
<xsl:namespace-alias 
	stylesheet-prefix="oaf"
	result-prefix="#default" />

<xsl:output method="xml"  indent="yes" encoding="UTF-8" omit-xml-declaration="yes"/>
<xsl:template match="/">

	 <xsl:for-each select="//oaf:OAF">
			<record>
				 <!-- Identifier 
							TODO Check prefixing
							-->
				<marc:datafield tag="024" ind1="7" ind2=" ">
					<marc:subfield code="a">G:(EU-Grant)<xsl:value-of select="./oaf:grant_agreement_number" /></marc:subfield>
					<marc:subfield code="d"><xsl:value-of select="./oaf:grant_agreement_number" /></marc:subfield>
					<marc:subfield code="2">CORDIS</marc:subfield>
				 </marc:datafield>
				 <marc:datafield tag="024" ind1="7" ind2=" ">
					<marc:subfield code="a">G:(EU-Call)<xsl:value-of select="./oaf:call_identifier" /></marc:subfield>
					<marc:subfield code="d"><xsl:value-of select="./oaf:call_identifier" /></marc:subfield>
					<marc:subfield code="2">CORDIS</marc:subfield>
				 </marc:datafield>

				<marc:datafield tag="035" ind1=" " ind2=" ">
					<marc:subfield code="a">G:(EU-Grant)<xsl:value-of select="./oaf:grant_agreement_number" /></marc:subfield>
				 </marc:datafield>

					<!-- Project title and duration -->
					<marc:datafield tag="150" ind1=" " ind2=" ">
					<marc:subfield code="a">
						<xsl:value-of select="./oaf:title" />
					</marc:subfield>
					<xsl:if test="./oaf:start_date != '' or ./oaf:end_date != ''">
						 <marc:subfield code="y"><xsl:value-of select="./oaf:start_date" /> - <xsl:value-of select="./oaf:end_date" /></marc:subfield>
					</xsl:if>
					</marc:datafield>

          <!-- Call identification -->
					<marc:datafield tag="372" ind1=" " ind2=" ">
					<marc:subfield code="a"><xsl:value-of select="./oaf:call_identifier" /></marc:subfield>
					<xsl:if test="./oaf:start_date != ''">
						 <marc:subfield code="s"><xsl:value-of select="./oaf:start_date" /></marc:subfield>
					</xsl:if>
					<xsl:if test="./oaf:end_date != ''">
						 <marc:subfield code="t"><xsl:value-of select="./oaf:end_date" /></marc:subfield>
					</xsl:if>
					</marc:datafield>

					<marc:datafield tag="450" ind1=" " ind2=" ">
						<marc:subfield code="a">
						<xsl:value-of select="./oaf:acronym" />
						</marc:subfield>
						<marc:subfield code="w">d</marc:subfield>
						<xsl:if test="./oaf:start_date != '' or ./oaf:end_date != ''">
						 	<marc:subfield code="y"><xsl:value-of select="./oaf:start_date" /> - <xsl:value-of select="./oaf:end_date" /></marc:subfield>
						</xsl:if>
					</marc:datafield>

					<!-- Funcing agency
							 TODO needs improvement
							 -->
					<marc:datafield tag="510" ind1="1" ind2=" ">
						<marc:subfield code="a">European Union</marc:subfield>
						<marc:subfield code="b">
               <xsl:value-of select="./oaf:fundedby" />
						</marc:subfield>
						<marc:subfield code="v">http://www.openaire.eu:8280/is/mvc/openaireOAI/oai.do</marc:subfield>
						<marc:subfield code="2">CORDIS</marc:subfield>
					</marc:datafield>


					<!-- Optional 1 / Optional 2 as footnotes
							 TODO What do they mean?
					-->
					<xsl:if test="./oaf:optional1 != ''">
						 <marc:datafield tag="680" ind1=" " ind2=" ">
							 <marc:subfield code="a">
							 <xsl:value-of select="./oaf:optional1" />
							 </marc:subfield>
						 </marc:datafield>
					</xsl:if>

					<xsl:if test="./oaf:optional2 != ''">
						 <marc:datafield tag="680" ind1=" " ind2=" ">
							 <marc:subfield code="a">
							 <xsl:value-of select="./oaf:optional2" />
							 </marc:subfield>
						 </marc:datafield>
					</xsl:if>


          <!-- 506 is actually a bibliographic footnote tag, but it
          seems most appropriate for the contents. -->
					<xsl:if test="./oaf:sc39 = 'true'">
						 <marc:datafield tag="506" ind1="0" ind2=" ">
							 <marc:subfield code="a">OpenAccess Mandate</marc:subfield>
							 <marc:subfield code="b">European Union</marc:subfield>
						 </marc:datafield>
					</xsl:if>

					<!-- Websites for the project -->
					<xsl:if test="./oaf:website != ''">
						 <marc:datafield tag="856" ind1="4" ind2=" ">
						 <marc:subfield code="u">
							 <xsl:value-of select="./oaf:website" />
							 </marc:subfield>
						 <marc:subfield code="y">Project Website</marc:subfield>
						 </marc:datafield>
					</xsl:if>
					<xsl:if test="./oaf:ec_project_website != ''">
						 <marc:datafield tag="856" ind1="4" ind2=" ">
						 <marc:subfield code="u">
							 <xsl:value-of select="./oaf:ec_project_website" />
							 </marc:subfield>
						 <marc:subfield code="y">EU Project Website</marc:subfield>
						 </marc:datafield>
					</xsl:if>

					<!-- add Autority collections + special CORDIS ccolleciton -->
					<marc:datafield tag="980" ind1=" " ind2=" ">
						 <marc:subfield code="a">G</marc:subfield>
					</marc:datafield>
					<marc:datafield tag="980" ind1=" " ind2=" ">
						 <marc:subfield code="a">CORDIS</marc:subfield>
					</marc:datafield>
					<marc:datafield tag="980" ind1=" " ind2=" ">
						 <marc:subfield code="a">AUTHORITY</marc:subfield>
					</marc:datafield>
			</record>
		</xsl:for-each>

    <!--
    <xsl:value-of select="//oaf:fundedby" />
    <xsl:value-of select="//oaf:optional1" />
    <xsl:value-of select="//oaf:optional2" />
    <xsl:value-of select="//oaf:sc39" />
    <xsl:value-of select="//oaf:start_date" />
    <xsl:value-of select="//oaf:end_date" />
    <xsl:value-of select="//oaf:projectid" />
    -->
  <!-- </xsl:for-each-group> -->

</xsl:template>
</xsl:stylesheet>
