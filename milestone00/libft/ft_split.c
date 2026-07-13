/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_split.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/26 18:33:37 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:20:07 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static size_t	count_words(char const *src, char c)
{
	size_t	cnt_words;
	size_t	idx;
	int		flag;

	idx = 0;
	cnt_words = 0;
	flag = 1;
	while (src[idx])
	{
		if (src[idx] != c)
		{
			if (flag)
				cnt_words++;
			flag = 0;
		}
		else
			flag = 1;
		idx++;
	}
	return (cnt_words);
}

static char	*copy_word(char const *src, size_t start, size_t len)
{
	char	*word;
	size_t	idx;

	word = (char *)malloc((len + 1) * sizeof(char));
	if (word == NULL)
		return (NULL);
	idx = 0;
	while (idx < len)
	{
		word[idx] = src[start + idx];
		idx++;
	}
	word[len] = '\0';
	return (word);
}

static void	free_result(char **result, size_t count)
{
	size_t	idx;

	idx = 0;
	while (idx < count)
	{
		free(result[idx]);
		idx++;
	}
	free(result);
}

static int	fill_result(char **res, char const *src, char c, size_t num_words)
{
	size_t	idx_src;
	size_t	idx_word;
	size_t	word_start;

	idx_src = 0;
	idx_word = 0;
	while (idx_word < num_words)
	{
		while (src[idx_src] && src[idx_src] == c)
			idx_src++;
		word_start = idx_src;
		while (src[idx_src] && src[idx_src] != c)
			idx_src++;
		res[idx_word] = copy_word(src, word_start, idx_src - word_start);
		if (res[idx_word] == NULL)
		{
			free_result(res, idx_word);
			return (0);
		}
		idx_word++;
	}
	res[idx_word] = NULL;
	return (1);
}

char	**ft_split(char const *src, char c)
{
	size_t	num_words;
	char	**result;

	if (src == NULL)
		return (NULL);
	num_words = count_words(src, c);
	result = (char **)malloc((num_words + 1) * sizeof(char *));
	if (result == NULL)
		return (NULL);
	if (!fill_result(result, src, c, num_words))
		return (NULL);
	return (result);
}
