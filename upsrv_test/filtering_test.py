
from testrunner import testcase
from testutils import mock

import dateutil.tz

from conary import conarycfg

from upsrv import config, app, db
from upsrv import filtering as F
from upsrv.db.models import Record

class CollectionTest(testcase.TestCaseWithWorkDir):
    def testQueryTree(self):
        q = F.AndOperator(
               # port=8080 for a given type of configurator
               F.AndOperator(
                   F.EqualOperator('latest_survey.survey_config.type', '0'),
                   F.EqualOperator('latest_survey.survey_config.value', '8080'),
                   F.LikeOperator('latest_survey.survey_config.key', '/port'),
               ),
               # name has substring either a or not e (super arbitrary) 
               F.OrOperator(
                   F.LikeOperator('latest_survey.rpm_packages.rpm_package_info.name', 'a'),
                   F.NotLikeOperator('latest_survey.rpm_packages.rpm_package_info.name', 'e'),
               )
        )

        # shorter form!
        q2 = F.AndOperator(
               F.ContainsOperator('latest_survey.survey_config', F.AndOperator(
                   F.EqualOperator('type', '0'),
                   F.EqualOperator('value', '8080'),
                   F.LikeOperator('key', '/port'),
               )),
               F.ContainsOperator('latest_survey.rpm_packages.rpm_package_info', F.OrOperator(
                   F.LikeOperator('name', 'a'),
                   F.NotLikeOperator('name', 'e'),
               ))
        )

        test1 = 'AND(AND(EQ(latest_survey.survey_config.type,0),EQ(latest_survey.survey_config.value,8080),LIKE(latest_survey.survey_config.key,/port)),OR(LIKE(latest_survey.rpm_packages.rpm_package_info.name,a),NOT_LIKE(latest_survey.rpm_packages.rpm_package_info.name,e)))'
        test2 = 'AND(CONTAINS(latest_survey.survey_config,AND(EQ(type,0),EQ(value,8080),LIKE(key,/port))),CONTAINS(latest_survey.rpm_packages.rpm_package_info,OR(LIKE(name,a),NOT_LIKE(name,e))))'
        self.assertEquals(q.asString(), test1)
        self.assertEquals(q2.asString(), test2)

        # Lexer...
        lexer = F.Lexer()
        tree = lexer.scan(test1)
        self.assertEquals(tree.asString(), test1)
        self.assertEquals(tree, q)

        # Simpler tests
        tests = [
            (F.EqualOperator('key', 'port'), 'EQ(key,port)'),
            (F.EqualOperator('key', r'a "quoted" value'),
                r'EQ(key,"a \"quoted\" value")'),
            (F.EqualOperator('key', r'Extra ( and ), backslash \ stray \n\r and "'),
                r'EQ(key,"Extra ( and ), backslash \\ stray \\n\\r and \"")'),
            # No need to add quotes around a word with \ in it
            (F.EqualOperator('key', r'with \ within'),
                r'EQ(key,with \\ within)'),
        ]
        for q, strrepr in tests:
            tree = lexer.scan(strrepr)
            self.assertEquals(tree, q)
            self.assertEquals(q.asString(), strrepr)
            self.assertEquals(tree.asString(), strrepr)

        # One-way tests - extra quotes that get stripped out etc
        tests = [
            (F.EqualOperator('key', r'with \ within'),
                r'EQ(key,"with \\ within")'),
            (F.EqualOperator('key', 'port'), 'EQ(key,"port")'),
            (F.EqualOperator('key', ' value with spaces '),
                ' EQ ( key ,  " value with spaces "  )'),
        ]
        for q, strrepr in tests:
            tree = lexer.scan(strrepr)
            self.assertEquals(tree, q)

        # Errors
        tests = [
            ('EQ(key,"port)', 'Closing quote not found'),
            ('abc', 'Unable to parse abc'),
            ('FOO(key,"port)', 'Unknown operator FOO'),
            ('EQ(key,port)junk', "Garbage found at the end of the expression: 'junk'"),
            ('EQ(key,port', 'Unable to parse EQ(key,port'),
        ]
        InvalidData = F.InvalidData
        for strrepr, err in tests:
            e = self.assertRaises(InvalidData, lexer.scan, strrepr)
            self.assertEquals(e.msg, err)

    def testFilterDateParser(self):
        queryFilter = 'GE(updated_time,"2014")'
        lexer = F.Lexer()
        qf = lexer.scan(queryFilter)
        expression = qf.expression(Record)
        self.assertEquals(str(expression.left.expression),
            "records.updated_time")
        self.assertEquals(expression.right.value.year, 2014)
        self.assertEquals(expression.right.value.month, 1)
        self.assertEquals(expression.right.value.day, 1)
        self.assertEquals(expression.right.value.hour, 0)
        self.assertEquals(expression.right.value.minute, 0)
        self.assertEquals(expression.right.value.second, 0)
        self.assertEquals(expression.right.value.microsecond, 0)
        self.assertTrue(isinstance(expression.right.value.tzinfo,
            dateutil.tz.tzutc))
