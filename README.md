# qidian_spider
1.create a mysql tabel with:
      CREATE TABLE `article`  (
        `article_id` int(11) NOT NULL,
        `title` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
        `author` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
        `article_type` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
        `subtypes` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        `status` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        `tags` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        `intro` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        `words_count` int(11) NULL DEFAULT NULL,
        `total_click` int(11) NULL DEFAULT NULL,
        `weekly_click` int(11) NULL DEFAULT NULL,
        `total_recommend` int(11) NULL DEFAULT NULL,
        `weekly_recommend` int(11) NULL DEFAULT NULL,
        `rating` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        `rating_count` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        `book_intro` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
        `chapter_count` int(11) NULL DEFAULT NULL,
        `honors` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
        `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
        PRIMARY KEY (`article_id`) USING BTREE
      ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

      SET FOREIGN_KEY_CHECKS = 1;

2.change mysql setting in pipeline.py 

3.create an new folder '/remain/001'  # using for recoerding

4.create an new folder '/msg'  # recoding message about url page and error

5.start with start_qidian_spider.py or cmdline
